CREATE VIEW "v_command" AS SELECT "command_id", "name", "owner_id" FROM "commands";
CREATE VIEW "v_users" AS SELECT "user_id", "name" FROM "users";
CREATE VIEW "v_user_cols" AS SELECT "user_id", "cols_order" FROM "users";
CREATE VIEW "v_personal_tasks" AS
SELECT "task_id", "description", "start_date", "end_date", "done", "col_id"
FROM "personal_tasks";

CREATE VIEW "v_command_cols" AS SELECT "command_id", "cols_order" FROM "commands";
CREATE VIEW "v_command_tasks" AS
SELECT "tasks"."task_id", "description", "start_date", "end_date", "done", "performer_id", "col_id", "commands_task"."command_id", "users"."name"
FROM "tasks"
INNER JOIN "commands_task"
ON "tasks"."task_id" = "commands_task"."task_id"
INNER JOIN "users"
ON "tasks"."performer_id" = "users"."user_id";

CREATE VIEW "v_group" AS
SELECT "groups"."group_id", "groups"."name", "color", "groups"."command_id", "manager_id", "user_id", "owner_id"
FROM "groups"
INNER JOIN "groups_user"
ON "groups"."group_id" = "groups_user"."group_id"
INNER JOIN "commands"
ON "groups"."command_id" = "commands"."command_id";