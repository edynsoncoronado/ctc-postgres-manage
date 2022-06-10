import os
import subprocess
import shlex
import psycopg2
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_postgres_db(db_host, db_name, db_restore, db_port, db_user, db_password):
    try:
        con = psycopg2.connect(
            dbname=db_name,
            port=db_port,
            user=db_user,
            host=db_host,
            password=db_password
        )
    except Exception as e:
        print(e)
        exit(1)
    
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        cur.execute("CREATE DATABASE {} ;".format(db_restore))
    except Exception as e:
        print(e)
        exit(1)
    
    return db_restore


def swap_after_restore(db_host, db_restore, db_name, db_template, db_port, db_user, db_password):
    try:
        con = psycopg2.connect(
            dbname=db_template,
            port=db_port,
            user=db_user,
            host=db_host,
            password=db_password
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        command = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "\
            f"WHERE datname = '{db_name}';"
        print(command)
        cur.execute(command)
        cur.execute("DROP DATABASE IF EXISTS {}".format(db_name))
        cur.execute('ALTER DATABASE "{}" RENAME TO "{}";'.format(db_restore, db_name))
    except Exception as e:
        print(e)
        exit(1)


def restore_postgres_db(user_server, pass_server, db_host, db_name, db_port, db_user, db_password, file_path):
    try:
        command_line = f'sshpass -p {pass_server} ssh -oStrictHostKeyChecking=no '\
            f'{user_server}@app2 '\
            f'pg_restore --no-owner --no-privileges --dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name} '\
            f'{file_path} -v'

        args = shlex.split(command_line)
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = process.communicate()[0]

        if int(process.returncode) != 0:
            print('Command failed. Return code : {}'.format(process.returncode))

        return output
    except Exception as e:
        print("Issue with the db restore : {}".format(e))


def backup_postgres_db(user_server, pass_server, db_host, db_name, db_port, db_user, db_password, file_path):
    try:
        command_line = f'sshpass -p {pass_server} ssh -oStrictHostKeyChecking=no '\
            f'{user_server}@app2 '\
            f'pg_dump --dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name} '\
            f'--no-owner '\
            f'-Fc -f {file_path} -v'
        print(command_line) 

        args = shlex.split(command_line)
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        if int(process.returncode) != 0:
            print('Command failed. Return code : {}'.format(process.returncode))
            exit(1)
        return output
    except Exception as e:
        print(e)
        exit(1)

def execute_main(action):
    logger = logging.getLogger(__name__)

    user_server = 'foobob'
    pass_server = 'foobob'

    db_host = os.environ['database_host']
    db_name = os.environ['database_orig']
    db_user = os.environ['database_user']
    db_port = 5432
    db_password = os.environ['database_pass']

    backup_file = 'backup.dump'
    db_restore = db_name + 'temporal'
    dest_db_template = 'template1'

    dest_db_host = os.environ['database_dest_host']
    dest_db_name = os.environ['database_dest_orig']
    dest_db_user = os.environ['database_dest_user']
    dest_db_port = 5432
    dest_db_password = os.environ['database_dest_pass']

    if action == 'backup':
        logger.info('Backing up {} database to {}'.format(db_user, backup_file))
        result = backup_postgres_db(
            user_server,
            pass_server,
            db_host,
            db_name,
            db_port,
            db_user,
            db_password,
            backup_file
        )
        for line in result.splitlines():
            logger.info(line)
        logger.info("Backup complete")

    elif action == 'restore1':
        logger.info("Creating temp database for restore : {}".format(db_restore))
        tmp_database = create_postgres_db(
            dest_db_host,
            dest_db_template,
            db_restore,
            dest_db_port,
            dest_db_user,
            dest_db_password
        )

    elif action == 'restore2':
        logger.info("Created temp database for restore : {}".format(db_restore))
        logger.info("Restore starting")
        result = restore_postgres_db(
                user_server,
                pass_server,
                dest_db_host,
                db_restore,
                dest_db_port,
                dest_db_user,
                dest_db_password,
                backup_file
        )
        for line in result.splitlines():
            logger.info(line)
            
    elif action == 'restore3':
        logger.info('Restore complete')
        logger.info("Switching restored database with new one : {} > {}".format(
            db_restore, dest_db_name
        ))
        swap_after_restore(
            dest_db_host,
            db_restore,
            dest_db_name,
            dest_db_template,
            dest_db_port,
            dest_db_user,
            dest_db_password
        )
        logger.info("Database restored and active.")
