from enum import StrEnum


class Permission(StrEnum):
    READ = "workspace:read"
    CRM_WRITE = "crm:write"
    COMMERCE_WRITE = "commerce:write"
    IMPORT = "imports:write"
    MARKETING_WRITE = "marketing:write"
    APPROVE = "actions:approve"
    TEAM = "team:manage"
    AUDIT = "audit:read"
    SCORE = "intelligence:score"
    INTEGRATION_WRITE = "integrations:write"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "OWNER": frozenset(Permission),
    "ADMIN": frozenset(Permission),
    "MARKETING_MANAGER": frozenset(
        {
            Permission.READ,
            Permission.CRM_WRITE,
            Permission.MARKETING_WRITE,
            Permission.AUDIT,
            Permission.SCORE,
        }
    ),
    "ANALYST": frozenset({Permission.READ}),
    "OPERATOR": frozenset(
        {Permission.READ, Permission.CRM_WRITE, Permission.COMMERCE_WRITE, Permission.IMPORT}
    ),
}
