.DEFAULT_GOAL := all

.PHONY: check test e2e mutate install all

install:
	pnpm install --frozen-lockfile

check:
	pnpm format:check
	pnpm stylelint
	pnpm lint
	pnpm typecheck
	pnpm knip
	pnpm depcruise
	pnpm jscpd
	pnpm fallow

test:
	pnpm test

e2e:
	pnpm e2e
	pnpm e2e:bdd

mutate:
	pnpm mutate

all: check test e2e
