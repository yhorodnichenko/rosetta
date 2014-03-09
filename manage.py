#!/usr/bin/env python
# -*- coding:utf8 -*-
import os

from framework import db
from application import app_factory

from pypm import ProjectManager


DEFAULT_CONFIG_FILE_PATH = os.path.expandvars(
    '$PROJECT_DIR/etc/configs/default_config.yml')

USER_CONFIG_FILE_PATH = os.path.expandvars(
    '$PROJECT_DIR/etc/configs/user_config.yml')


def create_application(custom_config_file_path=USER_CONFIG_FILE_PATH):
    if os.access(custom_config_file_path, os.R_OK):
        return app_factory.create_application(
            DEFAULT_CONFIG_FILE_PATH,
            custom_config_file_path)
    else:
        print("NOT_FOUND_CUSTOM_CONFIG_FILE_PATH:%s" % custom_config_file_path)
        return app_factory.create_application(
            DEFAULT_CONFIG_FILE_PATH)


pm = ProjectManager()

@pm.command(package_names=dict(type=str, nargs='+', help='파이썬 패키지 이름'))
def install_package(package_names):
    """
    파이썬 패키지 설치 후 requirement.txt 를 갱신합니다.
    """

    if not package_names:
        raise pm.ArgumentError('NO_PACKAGE_NAME')

    for package_name in package_names:
        pm.run_system_command('pip', ['install', package_name])

    pm.run_system_command(
        'pip', ['freeze', '> ./requirements.txt'])

@pm.command(config_file_path=dict(type=str, nargs=1, help='설정 파일 경로'))
def switch_config(config_file_path):
    """
    유저 설정 파일을 교체합니다.
    """

    pm.run_system_command(
        'cp', [config_file_path, USER_CONFIG_FILE_PATH])

@pm.command(script_file_path=dict(type=str, nargs=1, help='스크립트 파일 경로'))
def run_script(script_file_path):
    """
    스크립트를 실행합니다.
    """
    script_dir_path, script_name = os.path.split(script_file_path) 

    import sys
    sys.path.append(script_dir_path)
    execfile(script_file_path, {'__name__': '__main__'})

@pm.command(config_file_path=dict(type=str, flag='-c',
                                  default=USER_CONFIG_FILE_PATH,
                                  help='설정 파일 경로'))
def run_shell(config_file_path):
    """
    쉘을 실행합니다. app 과 db 에 접근할 수 있습니다.
    """

    app = create_application(config_file_path)
    pm.run_python_shell('Rosetta Shell', local_dict=dict(app=app, db=db))

@pm.command(config_file_path=dict(type=str, flag='-c',
                                  default=USER_CONFIG_FILE_PATH,
                                  help='설정 파일 경로'))
def reset_all_databases(config_file_path):
    """
    모든 데이터 베이스를 리셋합니다. 만약에 대비해 패스워드를 확인합니다.
    전체 리셋 패스워드를 지정하지 않았다면 사용할 수 없습니다.
    """

    app = create_application(config_file_path)

    print "#### reset all databases"
    print "* database uri: %s" % app.config['SQLALCHEMY_DATABASE_URI']
    for key, value in sorted(app.config['SQLALCHEMY_BINDS'].iteritems()):
        print " * bind_key: %s uri:%s" % (key, value)

    print "* reset_all_password:", 
    config_password = app.config['RESET_ALL_PASSWORD']
    if not config_password:
        raise pm.Error('NO_PERMISSION_TO_RESET_ALL_PASSWORD')

    input_password = raw_input()
    if input_password != config_password:
        raise pm.Error('WRONG_RESET_ALL_PASSWORD')

    db.drop_all()
    db.create_all()

@pm.command(config_file_path=dict(type=str, flag='-c',
                                  default=USER_CONFIG_FILE_PATH,
                                  help='설정 파일 경로'),
            port=dict(type=int, flag='-p', default=5000, help="포트 번호"))
def run_server(config_file_path, port):
    """
    서버를 실행합니다. 기본 포트는 5000번입니다.
    """

    app = create_application(config_file_path)
    app.run(port=port)


if __name__ == '__main__':
    import sys
    pm.run_command(sys.argv[1:])
