from DataTypes import *
import mysql.connector
import random

# Bundles together functions for probing a MySQL database to confirm
# whether it adheres to specific properties of a logical/relational schema.
# Can be used to verify that a MySQL database correctly implements a design.
class DataModelChecker:

    # Ctor sets the connection details for this model checker
    def __init__( self, host, username, password, database ):
        # TODO: Implement me!
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    # Predicate function that connects to the database and confirms
    # whether or not a list of attributes is set up as a (super)key for a given table
    # For example, if attributes contains table_name R and attributes [x, y],
    # this function returns true if (x,y) is enforced as a key in R
    # @see Util.Attributes
    # @pre the tables and attributes in attributes must already exist

    def confirmSuperkey(self, attributes):
        # TODO: Implement me!
        try:
            connection = mysql.connector.connect(host=self.host, user=self.username, password=self.password,
                                                 database=self.database)

            cursor = connection.cursor()
            table_name = attributes.table_name
            attribute_names = ','.join(attributes.attributes)

            if len(attribute_names) == 0:
                return True
            elif len(attribute_names) == 1:
                attribute_names = attribute_names
            else:
                attribute_names = ','.join(attributes.attributes)

            sql = f"SELECT {attribute_names} from {table_name};"
            cursor.execute(sql)
            x = 0

            result = cursor.fetchall()
            if len(result) == 0:
                p = len(attributes.attributes)
                result = []
                for i in range(p):
                    result.append(1)
                x = ','.join(map(str, result))
            elif len(attribute_names) == 1:
                x = result[0][0]
            else:
                x = result[0][0:]
                x = ','.join(map(str, x))

            for r in range(2):
                query = f"INSERT INTO {table_name} ({attribute_names}) VALUE ({x});"
                cursor.execute(query)

            cursor.close()
            connection.close()
            return False
        except mysql.connector.Error as e:
            x = str(e)
            if 'Duplicate entry' in x:
                return True
            return False

    # Predicate function that connects to the database and confirms
    # whether `referencing_attributes` is set up as a foreign
    # key that reference `referenced_attributes`
    # For example, if referencing_attributes contains table_name R and attributes [x, y]
    # and referenced_attributes contains table_name S and attributes [a, b]
    # this function returns true if (x,y) is enforced as a foreign key that references
    # (a,b) in R
    # @see Util.Attributes
    # @pre the tables and attributes in referencing_attributes and referenced_attributes must already exist
    def confirmForeignKey( self, referencing_attributes, referenced_attributes):
        # TODO: Implement me!
        f = ''
        b = []
        m = []
        c = 1
        try:
            connection = mysql.connector.connect(host=self.host, user=self.username, password=self.password,
                                                 database=self.database)
            cursor = connection.cursor()
            referencing_table_name = referencing_attributes.table_name
            referencing_attribute_names = ', '.join(referencing_attributes.attributes)
            referenced_table_name = referenced_attributes.table_name
            referenced_attribute_names = ', '.join(referenced_attributes.attributes)


            sql = f"SELECT {referenced_attribute_names} from {referenced_table_name};"
            cursor.execute(sql)
            result = cursor.fetchall()
            g = []

            if len(result) == 0:
                g = [x for x in range(len(referenced_attributes.attributes))]
                b = ",".join(map(str, g))
                query = f"INSERT INTO {referenced_table_name} ({referenced_attribute_names}) VALUES ({b});"
                cursor.execute(query)

            sql = f"SELECT {referenced_attribute_names} from {referenced_table_name};"
            cursor.execute(sql)
            result = cursor.fetchall()

            m = [2] * len(referencing_attributes.attributes)
            m = ",".join(map(str, m))
            query = f"INSERT INTO {referencing_table_name} ({referencing_attribute_names}) VALUES ({m});"
            cursor.execute(query)
            cursor.close()
            connection.close()

            return False
        except mysql.connector.Error as e:
            f = str(e)
            if "foreign key constraint fails" in f:
                cursor.close()
                connection.close()
                return True
            return False


    # Predicate function that connects to the database and confirms
    # whether or not `referencing_attributes` is set up as a foreign key
    # that reference `referenced_attributes` using a specific referential integrity `policy`
    # For example, if referencing_attributes contains table_name R and attributes [x, y]
    # and referenced_attributes contains table_name S and attributes [a, b]
    # this function returns true if (x,y) the provided policy is used to manage that foreign key
    # @see Util.Attributes, Util.RefIntegrityPolicy
    # @pre The foreign key is valid
    # @pre policy must be a valid Util.RefIntegrityPolicy
    def confirmReferentialIntegrity( self, referencing_attributes, referenced_attributes, policy):
        # TODO: Implement me!


        def get_column_data_types(cursor, table_name):
            # Get the data types of the columns in the specified table
            cursor.execute(f"DESCRIBE {table_name}")
            return {row[0]: row[1] for row in cursor.fetchall()}

        def get_test_value(data_type):
            # Return an appropriate test value based on the specified data type
            if "int" in data_type:
                return 1


        try:
            # Connect to the database
            connection = mysql.connector.connect(host=self.host, user=self.username, password=self.password, database=self.database)
            cursor = connection.cursor()

            # Get the table and column names for the referencing and referenced attributes
            referencing_table = referencing_attributes.table_name
            referencing_columns = referencing_attributes.attributes
            list_at = referenced_attributes.attributes
            referenced_table = referenced_attributes.table_name
            referenced_columns = referenced_attributes.attributes

            # Get the data types of the columns in both tables
            referencing_column_data_types = get_column_data_types(cursor, referencing_table)
            referenced_column_data_types = get_column_data_types(cursor, referenced_table)

            # Insert a test row into the referenced table
            insert_values = [get_test_value(referenced_column_data_types[col]) for col in referenced_columns]
            insert_values = ",".join(map(str, insert_values))
            insert_query = f"INSERT INTO {referenced_table} ({', '.join(referenced_columns)}) VALUES ({insert_values});"
            cursor.execute(insert_query)
            connection.commit()

            referenced_columns = ", ".join(map(str, referenced_columns))
            select_query = f"SELECT {referenced_columns} FROM {referenced_table};"
            cursor.execute(select_query)
            referenced_id = cursor.fetchall()
            if len(referenced_id) == 1:
                values = referenced_id[0]
            else:
                values = referenced_id[0]


            # Flatten the list of tuples and convert it to a string
            the = [item for sublist in referenced_id for item in sublist]
            referenced_id = ", ".join(map(str, [item for sublist in referenced_id for item in sublist]))

            insert_query = f"INSERT INTO {referencing_table} ({', '.join(referencing_columns)}) VALUES ({referenced_id});"
            cursor.execute(insert_query)
            connection.commit()
            if policy.operation == "DELETE":
                """
                If the foreign constraint is defined on delete, then the test row should be deleted from the parent table, 
                given the primary key's value
                """
                # Delete the test row in the referenced table
                try:
                    # Create a list of conditions for deleting values from all columns in the referenced table
                    delete_conditions = [f"{referenced_table}.{col}='{int(val)}'" for col, val in
                                         zip(list_at, the)]
                    delete_conditions_str = " AND ".join(delete_conditions)
                    delete_query = f"DELETE FROM {referenced_table} WHERE {delete_conditions_str};"
                    cursor.execute(delete_query)
                    connection.commit()

                    if policy.policy == "CASCADE":
                        where_conditions = [f"{referencing_table}.{col}=%s" for col in referencing_columns]
                        where_conditions_str = " AND ".join(where_conditions)

                        # Create the SELECT query
                        select_query = f"SELECT * FROM {referencing_table} WHERE {where_conditions_str}"
                        cursor.execute(select_query, values)
                        rows = cursor.fetchall()

                        if len(rows) == 0:
                            return True
                    elif policy.policy == "SET NULL":
                        where_conditions = [f"{referencing_table}.{col}" for col in referencing_columns]
                        where_conditions_str = " AND ".join(where_conditions)
                        select_query = f"SELECT * FROM {referencing_table} WHERE {where_conditions_str} IS NULL;"
                        cursor.execute(select_query)
                        rows = cursor.fetchall()
                        if len(rows):
                            return True
                except mysql.connector.Error as e:
                    c = str(e)
                    if (("foreign key constraint fails" in c.lower()) or ("on delete restrict" in c.lower())) and policy.policy == "REJECT":
                        return True

            elif policy.operation == "UPDATE":
                try:

                    update_conditions = [f"{col}=%s" for col in list_at]
                    update_conditions_str = ", ".join(update_conditions)

                    # Create a list of conditions for selecting the row to update based on all columns in the referenced table
                    where_conditions = [f"{col}=%s" for col in list_at]
                    where_conditions_str = " AND ".join(where_conditions)

                    update_query = f"UPDATE {referenced_table} SET {update_conditions_str} WHERE {where_conditions_str}"

                    # Create a list of new random values to update in the referenced table
                    update_values = [random.randint(1, 100) for _ in range(len(list_at))]
                    int_values = [x for x in update_values if isinstance(x, int)]
                    # Add the current values of the row to update to the end of the update_values list
                    update_values.extend(referenced_id.split(", "))
                    checkers = tuple(update_values)
                    cursor.execute(update_query, checkers)
                    connection.commit()


                    # Check if the behavior matches the expected behavior based on the provided policy
                    if policy.policy == "CASCADE":
                        # Check if the corresponding foreign key value in the referencing table was also updated
                        where_conditions = [f"{referencing_table}.{col}=%s" for col in referencing_columns]
                        where_conditions_str = " AND ".join(where_conditions)
                        select_query = f"SELECT * FROM {referencing_table} WHERE {where_conditions_str}"

                        int_values = tuple(int_values)

                        cursor.execute(select_query, int_values)
                        rows = cursor.fetchall()
                        if len(rows) >= 1:
                            return True


                    elif policy.policy == "SET NULL":
                        # Check if the corresponding foreign key value in the referencing table was set to NULL
                        where_conditions = [f"{referencing_table}.{col}" for col in referencing_columns]
                        where_conditions_str = " AND ".join(where_conditions)
                        select_query = f"SELECT * FROM {referencing_table} WHERE {where_conditions_str} IS NULL"
                        cursor.execute(select_query)
                        rows = cursor.fetchall()
                        if len(rows) >= 1:
                            return True

                except mysql.connector.Error as f:
                    c = str(f)
                    if policy.policy == "REJECT" and "on update restrict" in c.lower():
                        return True
            return False
        except mysql.connector.Error as e:
            x = str(e)
            return False


    # def generate_values(self, attributes):
    #     values = []
    #     for _ in range(len(attributes)):
    #         # Generate random integer values for the given number of attributes
    #         values.append(random.randint(1, 100))
    #     return values
    #
    # def generate_insert_query(self, table_name, attributes, values):
    #     value_string = ', '.join(str(value) for value in values)
    #     return f"INSERT INTO {table_name} ({', '.join(attributes)}) VALUES ({value_string})"






    # Predicate function that connects to the database and confirms
    # whether there or not `referencing_attributes` is set up in such as way as to
    # functionally determine `referenced_attributes`
    # For example, if referencing_attributes contains table_name R and attributes [x, y]
    # and referenced_attributes contains table_name S and attributes [a, b]
    # this function returns true if (x,y) is enforced to functionally determine (a,b) in R
    # @see Util.Attributes
    # @pre the tables and attributes in referencing_attributes and referenced_attributes must already exist
    def confirmFunctionalDependency( self, referencing_attributes, referenced_attributes ):
        # TODO: Implement me!
        def execute_query(query):
            cursor.execute(query)
            return cursor.fetchall()
        need = []

        try:
            cnx = mysql.connector.connect(user=self.username, password=self.password,
                                          host=self.host,
                                          database=self.database)
            cursor = cnx.cursor()

            ref_table = referencing_attributes.table_name
            ref_attrs = referencing_attributes.attributes
            refd_table = referenced_attributes.table_name
            refd_attrs = referenced_attributes.attributes


            v = self.confirmForeignKey(referencing_attributes, referenced_attributes)

            if v:
                return True

            # Extract the values from the referencing attributes
            query = f"SELECT {','.join(ref_attrs)} FROM {ref_table}"
            cursor.execute(query)
            ref_rows = cursor.fetchall()
            ref_tuples = [row for row in ref_rows]

            # Extract the values from the referenced attributes
            query = f"SELECT {','.join(refd_attrs)} FROM {refd_table}"
            cursor.execute(query)
            refd_rows = cursor.fetchall()
            refd_tuples = [row for row in refd_rows]

            # Combine the referencing and referenced tuples into a list of tuples
            tuples = [ref_tuple + refd_tuple for ref_tuple, refd_tuple in zip(ref_tuples, refd_tuples)]

            fd_dict = {}
            for tuple in tuples:
                ref_tuple = tuple[:len(ref_attrs)]
                refd_tuple = tuple[len(ref_attrs):]
                if ref_tuple not in fd_dict:
                    fd_dict[ref_tuple] = refd_tuple
                elif fd_dict[ref_tuple] != refd_tuple:
                    return False
            cnx.commit()
            cursor.close()
            cnx.close()

            # Check if the referencing table and the referenced table are the same

        except mysql.connector.Error as e:
            return False
        return True


    # Predicate function that connects to the database and confirms
    # whether or not any tuples in a given table are permitted to violate
    # a constraint expressed as a SQL snippet.
    # For example, given `R` and `x >= 0`, this function would return
    # true if it is not possible to add tuples to `R` with negative `x` values.
    # @pre sql_predicate must be valid SQL syntax that can be used as is in a WHERE condition
    # @pre table_name must exist in the database already
