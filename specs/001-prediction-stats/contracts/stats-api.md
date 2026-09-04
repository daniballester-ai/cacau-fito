# Contract: GET /stats

## Success response

**Status**: `200 OK`

**Body**:

```json
{
  "total": 12,
  "by_class": {
    "healthy": 5,
    "cssvd": 4,
    "anthracnose": 3
  }
}
```

- `total` is always present and equals the sum of `by_class` values.
- `by_class` always has one key per known class, even when its value is `0`.

### Example: no predictions recorded yet

```json
{
  "total": 0,
  "by_class": {
    "healthy": 0,
    "cssvd": 0,
    "anthracnose": 0
  }
}
```

## Failure response

**Status**: `503 Service Unavailable`

**Body**:

```json
{
  "detail": "Prediction stats are temporarily unavailable."
}
```

- Returned only when the underlying prediction history storage cannot be read.
- Never returned alongside a zeroed or partial `total`/`by_class` body — the two response shapes (success vs. failure) are mutually exclusive.

## Notes

- No request parameters (query, path, or body) — this is a simple, parameter-free read.
- No authentication required, consistent with the rest of the CacauFito PoC (`leaf-upload-frontend`'s "No authentication required" requirement).
