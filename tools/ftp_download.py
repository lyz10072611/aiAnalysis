import os
import ftplib
from ftplib import FTP


class FTPRecursiveDownloader:
    def __init__(self, host, username, password, port=21):
        self.ftp = FTP()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False

    def connect(self):
        """连接到FTP服务器"""
        try:
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
            self.connected = True
            print(f"✅ 成功连接到FTP服务器: {self.host}:{self.port}")
            print(f"欢迎信息: {self.ftp.getwelcome()}")
            return True
        except Exception as e:
            print(f"❌ 连接FTP服务器失败: {e}")
            return False

    def is_directory(self, name):
        """判断远程项目是否为目录[1](@ref)"""
        try:
            current_path = self.ftp.pwd()
            # 尝试切换到该项目，如果成功则是目录[1](@ref)
            self.ftp.cwd(name)
            self.ftp.cwd(current_path)  # 切换回原目录
            return True
        except Exception:
            return False

    def download_file(self, remote_file, local_file):
        """下载单个文件[5](@ref)"""
        try:
            # 确保本地目录存在
            local_dir = os.path.dirname(local_file)
            os.makedirs(local_dir, exist_ok=True)

            with open(local_file, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_file}', f.write)
            print(f"📥 下载文件: {remote_file} -> {local_file}")
            return True
        except Exception as e:
            print(f"❌ 下载失败 {remote_file}: {e}")
            return False

    def download_directory_recursive(self, remote_dir, local_dir):
        """递归下载整个目录结构[1,2](@ref)"""
        if not self.connected:
            print("❌ 未连接到FTP服务器")
            return False

        try:
            # 保存当前目录位置
            original_dir = self.ftp.pwd()

            # 切换到远程目录
            self.ftp.cwd(remote_dir)

            # 创建本地目录
            os.makedirs(local_dir, exist_ok=True)
            print(f"📁 进入目录: {remote_dir}")

            # 获取目录列表[1](@ref)
            items = self.ftp.nlst()

            for item in items:
                # 跳过当前目录和上级目录的表示
                if item in ['.', '..']:
                    continue

                local_path = os.path.join(local_dir, item)
                remote_path = os.path.join(remote_dir, item)

                if self.is_directory(item):
                    # 递归下载子目录
                    self.download_directory_recursive(item, local_path)
                else:
                    # 下载文件
                    self.download_file(item, local_path)

            # 返回上级目录
            self.ftp.cwd(original_dir)
            return True

        except Exception as e:
            print(f"❌ 处理目录 {remote_dir} 时出错: {e}")
            return False

    def get_full_tree(self, remote_dir='/', local_base_dir=r'/'):
        """下载完整的FTP目录树"""
        if not self.connect():
            return False

        try:
            success = self.download_directory_recursive(remote_dir, local_base_dir)
            if success:
                print("🎉 所有文件下载完成！")
            return success
        except Exception as e:
            print(f"❌ 下载过程中发生错误: {e}")
            return False
        finally:
            self.close()

    def close(self):
        """关闭FTP连接[5](@ref)"""
        if self.connected:
            try:
                self.ftp.quit()
                print("🔌 FTP连接已关闭")
            except Exception as e:
                print(f"⚠️ 关闭连接时出错: {e}")


def main():
    """主函数 - 使用您提供的FTP信息"""
    # 您的FTP服务器信息
    FTP_CONFIG = {
        'host': "8.140.22.128",
        'port': 88,
        'username': "daxing",
        'password': "Dxq123456"
    }

    # 下载配置
    REMOTE_DIR = '/daxing/tif/'  # 远程根目录，可根据需要修改
    LOCAL_DIR = r'J:\data\tif'  # 本地保存目录

    downloader = FTPRecursiveDownloader(**FTP_CONFIG)

    print("🚀 开始FTP递归下载任务")
    print(f"📡 服务器: {FTP_CONFIG['host']}:{FTP_CONFIG['port']}")
    print(f"📂 远程目录: {REMOTE_DIR}")
    print(f"💾 本地目录: {LOCAL_DIR}")
    print("-" * 50)

    try:
        # 开始下载
        success = downloader.get_full_tree(REMOTE_DIR, LOCAL_DIR)

        if success:
            print(f"✅ 下载完成！文件保存在: {os.path.abspath(LOCAL_DIR)}")
        else:
            print("❌ 下载过程中出现错误")

    except KeyboardInterrupt:
        print("\n⏹️ 用户中断下载")
    except Exception as e:
        print(f"💥 发生未预期错误: {e}")
    finally:
        downloader.close()


if __name__ == "__main__":
    main()