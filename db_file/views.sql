CREATE VIEW "v_command" AS SELECT "command_id", "name", "owner_id" FROM "commands";
CREATE VIEW "v_users" AS SELECT "user_id", "name" FROM "users";
CREATE VIEW "v_user_cols" AS SELECT "user_id", "cols_order" FROM "users";
