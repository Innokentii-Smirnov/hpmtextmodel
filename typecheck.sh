clear
mypy src \
  --follow-untyped-imports \
  --disallow-untyped-defs \
  --disallow-any-generics \
  --warn-unused-configs \
  --disallow-subclassing-any \
  --disallow-incomplete-defs \
  --check-untyped-defs \
  --disallow-untyped-decorators \
  --warn-redundant-casts \
  --warn-unused-ignores \
  --warn-return-any \
  --no-implicit-reexport \
  --strict-equality \
  --strict-bytes \
  --extra-checks
