# Longo (Mongo-like Java Engine)

Longo is a lightweight document database engine written in Java.

## What It Supports

- Document collections
- CRUD operations
- Query filters: `=`, `!=`, `>`, `>=`, `<`, `<=`, `in(...)`
- Logical filters with `and/or` in code
- Simple equality indexes per field
- Persistence to disk (`.bin`) using Java serialization

## Run

```bash
javac -d out src/main/java/com/clisonix/longo/*.java
java -cp out com.clisonix.longo.Main
```

## CLI Examples

```text
use prod
create users
index users email
insert users name=Ana age=31 email=ana@x.com
find users age>=30
update users where email=ana@x.com set city=Tirane premium=true
delete users where age<18
save
exit
```

## Notes

- This is a fast local engine and a strong base for a server layer.
- Next step can be a REST API wrapper and replication simulation.
