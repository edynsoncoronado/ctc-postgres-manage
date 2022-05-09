#!/usr/bin/python3

import boto3
import psycopg2
import subprocess
import logging

from decouple import config


#1) Generate backup from production
#2) Terminar sessiones de bd de analitics
#3) Eliminar la bd de analitics
#4) Restaurar backup de producciòn en analitics

def generate_backup_db(db_host, db_name, db_user, db_password, db_port, backup_file):
    try:
        process = subprocess.Popen(
            ['pg_dump',
             '--dbname=postgresql://{}:{}@{}:{}/{}'.format(db_user, db_password, db_host, db_port, db_name),
             '-f', backup_file,
             '--no-owner',
            '-v'],
            stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        if process.returncode != 0:
            print('Command failed. Return code : {}'.format(process.returncode))
            exit(1)
        return output
    except Exception as e:
        print(e)
        exit(1)


def main():
    logger = logging.getLogger(__name__)

    db_host = config('db_host')
    db_name = config('db_name')
    db_user = config('db_user')
    db_password = config('db_password')
    db_port = config('db_port')
    backup_file = config('backup_file')

    result = generate_backup_db(
        db_host,
        db_name,
        db_user,
        db_password,
        db_port,
        backup_file
    )

    for line in result.splitlines():
        logger.info(line)
    
    logger.info("Backup complete")


if __name__ == '__main__':
    main()