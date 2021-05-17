CREATE VIEW "v_users" AS SELECT "user_id", "name" FROM "users";

CREATE VIEW "v_users_login" AS SELECT "user_id", "name", "login" FROM "users";

CREATE VIEW "v_user_cols" AS SELECT "user_id", "cols_order" FROM "users";

CREATE VIEW "v_personal_tasks" AS
SELECT "task_id", "description", "start_date", "end_date", "done", "col_id"
FROM "personal_tasks";

CREATE VIEW "v_command" AS 
SELECT "commands"."command_id", "name", "owner_id", "user_id"
FROM "commands"
INNER JOIN "commands_user"
ON "commands_user"."command_id" = "commands"."command_id";

CREATE VIEW "v_command_cols" AS SELECT "command_id", "cols_order" FROM "commands";

CREATE VIEW "v_command_tasks" AS
SELECT "tasks"."task_id", "description", "start_date", "end_date", "done", "performer_id", "col_id", "commands_task"."command_id", "users"."name", "commands"."owner_id"
FROM "tasks"
INNER JOIN "commands_task"
ON "tasks"."task_id" = "commands_task"."task_id"
INNER JOIN "users"
ON "tasks"."performer_id" = "users"."user_id"
INNER JOIN "commands"
ON "commands_task"."command_id" = "commands"."command_id";

CREATE VIEW "v_group" AS
SELECT "groups"."group_id", "groups"."name", "color", "groups"."command_id",
        "groups"."owner_id", "blocked", "user_id", "commands"."owner_id" as "command_owner_id"
FROM "groups"
INNER JOIN "groups_user"
ON "groups"."group_id" = "groups_user"."group_id"
INNER JOIN "commands"
ON "groups"."command_id" = "commands"."command_id";

CREATE VIEW "v_group_cols" AS SELECT "group_id", "cols_order" FROM "groups";

CREATE VIEW "v_group_tasks" AS
SELECT "tasks"."task_id", "description", "start_date", "end_date", "done", "performer_id",
        "col_id", "groups_task"."group_id", "users"."name", "groups"."owner_id"
FROM "tasks"
INNER JOIN "groups_task"
ON "tasks"."task_id" = "groups_task"."task_id"
INNER JOIN "users"
ON "tasks"."performer_id" = "users"."user_id"
INNER JOIN "groups"
ON "groups_task"."group_id" = "groups"."group_id";
