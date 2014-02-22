#!/usr/bin/env python
# -*- coding:utf8 -*-
import pytest

from rosetta import db, app_factory, command_manager

def create_app():
    try:
        return app_factory.create_main_app()
    except Environment.Error:
        print "#### no active config"
        print "\t./mange.py switch_config "\
              "rosetta/data/$(TARGET)_config.yml"
        raise command_manager.Error('NO_ACTIVE_CONFIG')

@command_manager.command(package_names=dict(type=str, nargs='+', help='파이썬 패키지 이름'))
def install_package(package_names):
    """
    파이썬 패키지 설치 후 requirement.txt 를 갱신합니다.
    """

    if not package_names:
        raise CommandArgumentError('NO_PACKAGE_NAME')

    for package_name in package_names:
        command_manager.run_program('pip', ['install', package_name])

    command_manager.run_program('pip', ['freeze', '> requirements.txt'])

@command_manager.command(config_path=dict(type=str, nargs=1, help='활성화 설정 파일 경로'))
def switch_config(config_path):
    """
    active_config.yml 설정 파일을 교체합니다.
    """

    command_manager.run_program('cp', [config_path[0], 'active_config.yml'])

@command_manager.command(script_path=dict(type=str, nargs=1, help='실행 스크립트 파일 경로'))
def run_script(script_path):
    """
    스크립트를 실행합니다.
    """

    execfile(script_path[0], {'__name__': '__main__'})

@command_manager.command()
def run_shell():
    """
    쉘을 실행합니다. app 과 db 에 접근할 수 있습니다.
    """

    app = app_factory.create_main_app()
    command_manager.run_python_shell('Rosetta Shell', local_dict=dict(app=app, db=db))

@command_manager.command()
def reset_all_databases():
    """
    모든 데이터 베이스를 리셋합니다. 만약에 대비해 패스워드를 확인합니다.
    전체 리셋 패스워드를 지정하지 않았다면 사용할 수 없습니다.
    """

    app = app_factory.create_main_app()

    print "#### reset all databases"
    print "* database uri: %s" % app.config['SQLALCHEMY_DATABASE_URI']
    for key, value in sorted(app.config['SQLALCHEMY_BINDS'].iteritems()):
        print " * bind_key: %s uri:%s" % (key, value)

    print "* reset_all_password:", 
    config_password = app.config['RESET_ALL_PASSWORD']
    if not config_password:
        raise command_manager.Error('NO_PERMISSION_TO_RESET_ALL_PASSWORD')

    input_password = raw_input()
    if input_password != config_password:
        raise command_manager.Error('WRONG_RESET_ALL_PASSWORD')

    db.drop_all()
    db.create_all()

@command_manager.command(port=dict(type=int, default=5000, help="포트 번호"))
def run_server(port):
    """
    서버를 실행합니다. 기본 포트는 5000번입니다.
    """

    app = app_factory.create_main_app()
    app.run_server(port=port)


if __name__ == '__main__':
    import sys
    command_manager.run_command(sys.argv[1:])