# myRobot

这是一个基于 ROS 2 Humble + MoveIt 2 的机械臂工作区，里面包含两套配置：

- `mybot`：对应 `six_arm`
- `mydummy`：对应 `mydummy_description`

如果你只是想先把项目跑起来，优先按下面的“最快跑通”步骤做，不要一上来先跑 `demo.launch.py`。

## 运行环境

本文按下面环境整理，并在当前工作区里实际验证过构建命令：

- Ubuntu `22.04`
- ROS 2 `Humble`
- MoveIt 2
- Gazebo Classic（仅在需要仿真时）

## 目录说明

这个仓库本身就是一个 ROS 2 workspace，目录大致如下：

- `src/mybot`：`six_arm` 的 MoveIt 配置包
- `src/mybot_description`：`six_arm` 的 URDF 描述包
- `src/mydummy`：`mydummy_description` 的 MoveIt 配置包
- `src/mydummy_description`：`mydummy` 的 URDF 描述包

下面的命令默认工作区路径是 `~/myRobot`。如果你的路径不一样，替换成自己的路径即可。

## 依赖安装

第一次在新机器上跑，先装依赖：

```bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-humble-desktop \
  ros-humble-moveit \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-joint-state-publisher-gui \
  ros-humble-xacro
```

如果这台机器还没初始化过 `rosdep`，再执行一次：

```bash
sudo rosdep init
rosdep update
```

然后安装工作区依赖：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
rosdep install --from-paths src --ignore-src -r -y
```

## 构建

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
colcon build --symlink-install
source install/setup.bash
```

后面每开一个新终端，都建议先执行：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
source install/setup.bash
```

## 最快跑通

### 方式 1：推荐，分 3 个终端启动 `mybot`

终端 1：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
source install/setup.bash
ros2 launch mybot rsp.launch.py
```

终端 2：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
source install/setup.bash
ros2 launch mybot move_group.launch.py
```

终端 3：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
source install/setup.bash
ros2 launch mybot moveit_rviz.launch.py
```

正常情况下：

- 终端 1 会启动 `robot_state_publisher`
- 终端 2 会看到 `You can start planning now!`
- 终端 3 会打开 RViz，并加载 MoveIt 插件

关闭时对每个终端按 `Ctrl+C` 即可。

### 方式 2：把 `mybot` 换成 `mydummy`

如果你想跑 `mydummy`，上面 3 条命令里的包名全部换成 `mydummy`：

```bash
ros2 launch mydummy rsp.launch.py
ros2 launch mydummy move_group.launch.py
ros2 launch mydummy moveit_rviz.launch.py
```

### 只想先确认后端能不能起来

如果你当前机器没有图形界面，或者只是想先确认配置没问题，只跑前两个终端即可：

- `rsp.launch.py`
- `move_group.launch.py`

这两个入口在当前工作区里已经验证过可以正常拉起。

## 常用 launch 文件

### `mybot` 包

- `ros2 launch mybot rsp.launch.py`
  - 发布 `robot_description` 和 TF
- `ros2 launch mybot move_group.launch.py`
  - 启动 MoveIt 规划后端
- `ros2 launch mybot moveit_rviz.launch.py`
  - 启动 RViz 的 MoveIt 界面
- `ros2 launch mybot my_moveit_rviz.launch.py`
  - 自定义入口，同时拉起 `move_group` 和 RViz
- `ros2 launch mybot gazebo.launch.py`
  - 启动 Gazebo Classic 仿真
- `ros2 launch mybot warehouse_db.launch.py`
  - 启动 MoveIt warehouse 数据库
- `ros2 launch mybot setup_assistant.launch.py`
  - 打开 MoveIt Setup Assistant

### `mydummy` 包

- `ros2 launch mydummy rsp.launch.py`
- `ros2 launch mydummy move_group.launch.py`
- `ros2 launch mydummy moveit_rviz.launch.py`
- `ros2 launch mydummy my_moveit_rviz.launch.py`
- `ros2 launch mydummy gazebo.launch.py`
- `ros2 launch mydummy warehouse_db.launch.py`
- `ros2 launch mydummy setup_assistant.launch.py`

两套包的启动方式是对称的，区别主要在机器人模型不同。

## Gazebo 仿真

如果你想进 Gazebo Classic：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
source install/setup.bash
ros2 launch mybot gazebo.launch.py
```

或者：

```bash
ros2 launch mydummy gazebo.launch.py
```

注意：

- 这里用的是 `gazebo`，也就是 Gazebo Classic，不是新版 Ignition / Gazebo Sim
- Gazebo 需要图形界面环境

## 当前已知情况

当前仓库里不建议把 `demo.launch.py` 当成第一启动入口。

原因是它会额外拉起 `ros2_control_node`，而现有 URDF/ros2_control 配置里同时带有 Gazebo 相关硬件插件，直接跑时容易在加载 `gazebo_ros2_control/GazeboSystem` 时退出。为了保证新用户第一次就能跑起来，建议先按上面的分步启动方式使用。

如果后面你把这部分控制链路整理好了，再把默认入口切回：

```bash
ros2 launch mybot demo.launch.py
```

或：

```bash
ros2 launch mydummy demo.launch.py
```

## 常见问题

### 1. 提示 `package not found`

先确认两件事：

- 你是在工作区根目录 `~/myRobot` 下构建的
- 你当前终端已经执行过 `source /opt/ros/humble/setup.bash` 和 `source ~/myRobot/install/setup.bash`

### 2. RViz 没出来

- 确认当前机器有桌面环境
- 终端里直接执行 `rviz2` 看能不能正常打开
- 如果你是远程连接，确认图形转发已经配好

### 3. Gazebo 命令不存在

说明 Gazebo Classic 依赖没装全，重新执行上面的依赖安装命令即可。

### 4. 改完代码后没有生效

重新构建并重新 source：

```bash
source /opt/ros/humble/setup.bash
cd ~/myRobot
colcon build --symlink-install
source install/setup.bash
```
