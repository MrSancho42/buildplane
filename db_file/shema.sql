/* Користувачі */
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"  INTEGER PRIMARY KEY AUTOINCREMENT,
	"login"    TEXT UNIQUE NOT NULL,
	"password" TEXT NOT NULL,
	"name" TEXT NOT NULL,
	"cols_order" TEXT
);



/* Команди */
CREATE TABLE IF NOT EXISTS "commands" (
	"command_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"name"       TEXT NOT NULL,
	"owner_id"   INTEGER NOT NULL,
	"cols_order" TEXT,
	FOREIGN KEY ("owner_id") REFERENCES "users" ("user_id") ON UPDATE CASCADE

);

/* Проміжна таблиця між командами та користувачами
де вказано які користувачі у яких командах */
CREATE TABLE IF NOT EXISTS "commands_user" (
	"user_id"    INTEGER NOT NULL,
	"command_id" INTEGER NOT NULL,
	FOREIGN KEY ("user_id") REFERENCES "users" ("user_id"),
	FOREIGN KEY ("command_id") REFERENCES "commands" ("command_id")
);

/* Інвайти
status=True - інвайт активний, проте його не прийняли
status=False - інвайт було відхилено */
CREATE TABLE IF NOT EXISTS "invite" (
	"user_id"    INTEGER NOT NULL,
	"command_id" INTEGER NOT NULL,
	"status" INTEGER DEFAULT 1 NOT NULL,
	FOREIGN KEY ("user_id") REFERENCES "users" ("user_id"),
	FOREIGN KEY ("command_id") REFERENCES "commands" ("command_id")
);



/* Групи команд */
CREATE TABLE IF NOT EXISTS "groups" (
	"group_id"   INTEGER PRIMARY KEY AUTOINCREMENT,
	"name"       TEXT NOT NULL,
	"color"      TEXT NOT NULL,
	"command_id" INTEGER NOT NULL,
	"manager_id" INTEGER NOT NULL,
	"blocked" INTEGER DEFAULT 0 NOT NULL,
	"cols_order" TEXT,
	FOREIGN KEY ("command_id") REFERENCES "commands" ("command_id"),
	FOREIGN KEY ("manager_id") REFERENCES "users" ("user_id")
);

/* Проміжна таблиця між групами та користувачами
де вказано які користувачі у яких групах */
CREATE TABLE IF NOT EXISTS "groups_user" (
	"user_id"  INTEGER NOT NULL,
	"group_id" INTEGER NOT NULL,
	FOREIGN KEY ("user_id") REFERENCES "users" ("user_id"),
	FOREIGN KEY ("group_id") REFERENCES "groups" ("group_id")
);



/* Kanban-колонки */
CREATE TABLE IF NOT EXISTS "cols" (
	"col_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"name"   TEXT NOT NULL
);



/* Особисті завдання користувачів */
CREATE TABLE IF NOT EXISTS "personal_tasks" (
	"task_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"description" TEXT NOT NULL,
	"start_date" TEXT,
	"end_date" TEXT,
	"done" INTEGER DEFAULT 0 NOT NULL,
	"user_id" INTEGER NOT NULL,
	"col_id" INTEGER NOT NULL,
	FOREIGN KEY ("user_id") REFERENCES "users" ("user_id"),
	FOREIGN KEY ("col_id") REFERENCES "cols" ("col_id")
);



/* Завдання команд і груп */
CREATE TABLE IF NOT EXISTS "tasks" (
	"task_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"description" TEXT NOT NULL,
	"start_date" TEXT,
	"end_date" TEXT,
	"done" INTEGER DEFAULT 0 NOT NULL,
	"performer_id" INTEGER NOT NULL,
	"col_id" INTEGER NOT NULL,
	FOREIGN KEY ("performer_id") REFERENCES "users" ("user_id"),
	FOREIGN KEY ("col_id") REFERENCES "cols" ("col_id")
);

/* Завдання команд */
CREATE TABLE IF NOT EXISTS "commands_task" (
	"task_id" INTEGER NOT NULL,
	"command_id" INTEGER NOT NULL,
	FOREIGN KEY ("task_id") REFERENCES "tasks" ("task_id"),
	FOREIGN KEY ("command_id") REFERENCES "commands" ("command_id")
);

/* Завдання груп */
CREATE TABLE IF NOT EXISTS "groups_task" (
	"task_id" INTEGER NOT NULL,
	"group_id" INTEGER NOT NULL,
	FOREIGN KEY ("task_id") REFERENCES "tasks" ("task_id"),
	FOREIGN KEY ("group_id") REFERENCES "groups" ("group_id")
);



/* Особисті події користувачів */
CREATE TABLE IF NOT EXISTS "personal_events" (
	"event_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"description" TEXT NOT NULL,
	"date" TEXT,
	"done" INTEGER DEFAULT 0 NOT NULL,
	"user_id" INTEGER NOT NULL,
	FOREIGN KEY ("user_id") REFERENCES "users" ("user_id")
);



/* Події груп і команд */
CREATE TABLE IF NOT EXISTS "events" (
	"event_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"description" TEXT NOT NULL,
	"date" TEXT
);

/* Призначені користувачам події */
CREATE TABLE IF NOT EXISTS "users_event" (
	"event_id" INTEGER NOT NULL,
	"done" INTEGER DEFAULT 0 NOT NULL,
	"user_id" INTEGER NOT NULL,
	FOREIGN KEY ("event_id") REFERENCES "events" ("event_id"),
	FOREIGN KEY ("user_id") REFERENCES "users" ("user_id")
);

/* Події команд */
CREATE TABLE IF NOT EXISTS "commands_event" (
	"event_id" INTEGER NOT NULL,
	"command_id" INTEGER NOT NULL,
	FOREIGN KEY ("event_id") REFERENCES "events" ("event_id"),
	FOREIGN KEY ("command_id") REFERENCES "commands" ("command_id")
);

/* Події груп */
CREATE TABLE IF NOT EXISTS "groups_event" (
	"event_id" INTEGER NOT NULL,
	"group_id" INTEGER NOT NULL,
	FOREIGN KEY ("event_id") REFERENCES "events" ("event_id"),
	FOREIGN KEY ("group_id") REFERENCES "groups" ("group_id")
);
