CREATE VIEW "v_command" AS SELECT "command_id", "name", "owner_id" FROM "commands";
CREATE VIEW "v_users" AS SELECT "user_id", "name" FROM "users";
CREATE VIEW "v_user_cols" AS SELECT "user_id", "cols_order" FROM "users";
CREATE VIEW "v_personal_tasks" AS
SELECT "task_id", "description", "start_date", "end_date", "done", "col_id"
FROM "personal_tasks";
