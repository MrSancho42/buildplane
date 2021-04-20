BEGIN TRANSACTION;
INSERT INTO "users" VALUES (1,'mrs','b21dabb4c22d87c7e22f179206f3fa06efe0e6379df60ee5cfca87bea6efd236','Сашко',NULL); --Пароль mrs
INSERT INTO "users" VALUES (2,'s0fko','a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3','Софійка',NULL); --Пароль 123
INSERT INTO "commands" VALUES (1,'Command 1',1,NULL);
INSERT INTO "commands" VALUES (2,'Command 2',2,NULL);
INSERT INTO "commands_user" VALUES (1,1);
INSERT INTO "commands_user" VALUES (1,2);
INSERT INTO "commands_user" VALUES (2,1);
INSERT INTO "commands_user" VALUES (2,2);
COMMIT;
