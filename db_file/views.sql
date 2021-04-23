CREATE VIEW "v_command" AS SELECT "command_id", "name", "owner_id" FROM "commands";
CREATE VIEW "v_users" AS SELECT "user_id", "name" FROM "users";
CREATE VIEW "v_user_cols" AS SELECT "user_id", "cols_order" FROM "users";
CREATE VIEW "v_personal_tasks" AS
SELECT "personal_tasks"."task_id", "personal_tasks"."description",
        "personal_tasks"."start_date", "personal_tasks"."end_date",
        "personal_tasks"."done", "personal_tasks"."user_id",
        "personal_tasks"."col_id", "users"."name"
FROM "personal_tasks"
INNER JOIN "users"
ON "personal_tasks"."user_id" = "users"."user_id";
