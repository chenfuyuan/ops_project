# Naming Rules

Use names that express stable domain meaning and boundary responsibility.

## Directory naming
- Use domain-oriented, capability-oriented, or responsibility-oriented names.
- Prefer names that stay valid as implementation details change.
- Avoid vague buckets such as `misc`, `utils`, `common2`, or `temp`.

## Port naming
Name ports by the business capability they provide, not by transport, vendor, or SDK.

Good examples:
- `ContextReader`
- `ContentWriter`
- `ArtifactRepository`
- `TextComposer`

Avoid:
- `HttpPort`
- `SearchApiPort`
- `OpenAIAdapterPort`
- `SDKGateway`

## Infrastructure implementation naming
Name adapters by boundary responsibility plus provider or transport role.

Good examples:
- `LocalCapabilityContextReader`
- `HttpCapabilityContextReader`
- `SqlArtifactRepository`
- `ExternalValidationClient`

## General naming rule
Generated names should help a reader answer:
- What business or system responsibility does this own?
- Which boundary is this on?
- Is this an interface, an adapter, or a business object?

If a name only describes a technical mechanism and not the responsibility, it is probably too weak.
