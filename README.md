# ITNSA

Website for [itnsa.cn](https://itnsa.cn)

## Commands

Flask-migrate commands:

```bash
flask --app itnsa db init
flask --app itnsa db migrate -m "init"
flask --app itnsa db upgrade
```

Custom flask commands:

```bash
flask --app itnsa database create
flask --app itnsa database drop
flask --app itnsa create-roles
flask --app itnsa create-admin
```
