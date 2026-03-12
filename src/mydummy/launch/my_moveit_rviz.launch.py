from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_moveit_rviz_launch

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from moveit_configs_utils.launch_utils import (
    add_debuggable_node,
    DeclareBooleanLaunchArg,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 使用MoveItConfigsBuilder构建MoveIt配置
    # 第一个参数是SRDF中定义的robot name，第二个参数是MoveIt配置包名
    moveit_config = MoveItConfigsBuilder("mydummy_description", package_name="mydummy").to_moveit_configs()

    ld = LaunchDescription()

    # 启动move_group节点，提供运动规划服务
    my_generate_move_group_launch(ld, moveit_config)
    # 启动rviz可视化界面
    my_generate_moveit_rviz_launch(ld, moveit_config)

    return ld


def my_generate_move_group_launch(ld, moveit_config):
    """启动move_group节点，该节点是MoveIt的核心，负责运动规划、碰撞检测等"""

    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(
        DeclareBooleanLaunchArg("allow_trajectory_execution", default_value=True)
    )
    ld.add_action(
        DeclareBooleanLaunchArg("publish_monitored_planning_scene", default_value=True)
    )
    # 加载非默认的MoveGroup功能（空格分隔）
    ld.add_action(DeclareLaunchArgument("capabilities", default_value=""))
    # 禁用这些默认的MoveGroup功能（空格分隔）
    ld.add_action(DeclareLaunchArgument("disable_capabilities", default_value=""))

    # 不要从/joint_states复制动态信息到内部机器人监控
    # 默认为false，因为move_group中几乎没有依赖此信息的内容
    ld.add_action(DeclareBooleanLaunchArg("monitor_dynamics", default_value=False))

    should_publish = LaunchConfiguration("publish_monitored_planning_scene")

    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": LaunchConfiguration("allow_trajectory_execution"),
        # 注意：包装以下值是必要的，以便参数值可以为空字符串
        "capabilities": ParameterValue(
            LaunchConfiguration("capabilities"), value_type=str
        ),
        "disable_capabilities": ParameterValue(
            LaunchConfiguration("disable_capabilities"), value_type=str
        ),
        # 发布物理机器人的规划场景，以便rviz插件可以获取实际的机器人状态
        "publish_planning_scene": should_publish,
        "publish_geometry_updates": should_publish,
        "publish_state_updates": should_publish,
        "publish_transforms_updates": should_publish,
        "monitor_dynamics": False,
    }

    move_group_params = [
        moveit_config.to_dict(),
        move_group_configuration,
    ]
    # 使用仿真时间，与Gazebo同步
    move_group_params.append({"use_sim_time": True})

    add_debuggable_node(
        ld,
        package="moveit_ros_move_group",
        executable="move_group",
        commands_file=str(moveit_config.package_path / "launch" / "gdb_settings.gdb"),
        output="screen",
        parameters=move_group_params,
        extra_debug_args=["--debug"],
        # 设置显示变量，以防内部使用了OpenGL代码
        additional_env={"DISPLAY": ":0"},
    )
    return ld


def my_generate_moveit_rviz_launch(ld, moveit_config):
    """启动rviz可视化界面，加载MoveIt插件用于交互式运动规划"""

    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(
        DeclareLaunchArgument(
            "rviz_config",
            default_value=str(moveit_config.package_path / "config/moveit.rviz"),
        )
    )

    rviz_parameters = [
        moveit_config.planning_pipelines,
        moveit_config.robot_description_kinematics,
    ]
    # 使用仿真时间，与Gazebo同步
    rviz_parameters.append({"use_sim_time": True})

    add_debuggable_node(
        ld,
        package="rviz2",
        executable="rviz2",
        output="log",
        respawn=False,
        arguments=["-d", LaunchConfiguration("rviz_config")],
        parameters=rviz_parameters,
    )

    return ld
