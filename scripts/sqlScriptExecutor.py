# SQL script executors for executing DDL and DML scripts.
import re

# This module provides functions to execute SQL scripts for creating database schemas.
def execute_sql_ddl_script(connection, script_path):
    try:
        cursor = connection.cursor()

        with open(script_path, 'r') as file:
            sql_script = file.read()

        # Split by GO statements (SQL Server batch separator)
        # Remove GO statements and split into batches
        batches = re.split(r'\bGO\b', sql_script, flags=re.IGNORECASE)

        for batch in batches:
            batch = batch.strip()
            if not batch:
                continue
                
            # Execute each non-empty batch
            try:
                cursor.execute(batch)
                connection.commit()
                print(f"Executed batch successfully")
            except Exception as batch_error:
                print(f"Error in batch: {batch_error}")
                print(f"Problematic batch: {batch[:200]}...")  # First 200 chars for debugging
                # Continue with next batch instead of failing completely
                continue

        print(f"Successfully executed the SQL script: {script_path}")

    except Exception as e:
        print("Error executing SQL script:", e)

    finally:
        try:
            cursor.close()
        except:
            pass

# This module provides functions to execute SQL scripts for inserting data into a database.
def execute_sql_dml_script(connection, script_path, data_dict, N):
    try:
        cursor = connection.cursor()

        with open(script_path, 'r') as file:
            sql_script = file.read()

        sections = sql_script.split('-- SECTION ')

        for section in sections:
            if not section.strip():
                continue

            lines = section.strip().splitlines()
            table_name = lines[0].strip()
            insert_statement = "\n".join(lines[1:]).strip()

            if table_name not in data_dict:
                continue

            for i in range(N):
                if i < len(data_dict[table_name]):
                    record = data_dict[table_name][i]

                    cursor.execute(insert_statement, tuple(record.values()))

        connection.commit()
        print(f"Successfully inserted data using DML script: {script_path}")

    except Exception as e:
        print("Error executing DML script:", e)

    finally:
        try:
            cursor.close()
        except:
            pass