# URL Update: [State Abbreviation] - [State Name]

## Document: [Document Title]

### Current URL (Broken)
```
[Current broken URL from states.json]
```

**Validation Result:**
- HTTP Status: [404/403/500/etc]
- Content Type: [what was returned]
- File Size: [size or "not retrieved"]
- Error: [description of issue]

---

### Research Process

**Date Researched:** YYYY-MM-DD
**Researcher:** [Name or "Claude Code"]

**Steps Taken:**
1. Visited [state education agency website]
2. Navigated to [science/standards section]
3. Found [current standards page]
4. Located [document download link]

**Official Source Page:** [URL of page containing the document link]

---

### Proposed URL (Working)
```
[New working URL]
```

**Verification:**
- HTTP Status: 200 OK
- Content Type: application/pdf
- File Size: [size in KB/MB]
- Verification Date: YYYY-MM-DD
- Verified By: [Manual browser test / validation script]

---

### Changes to states.json

**JSON Patch:**
```json
{
  "state": "[STATE_ABBREV]",
  "document_index": [0-based index],
  "changes": {
    "url": "[new URL]",
    "url_source": "[official source page]",
    "last_verified": "YYYY-MM-DD"
  }
}
```

---

### Additional Notes

- **Redirects:** [List redirect chain if any]
- **Alternative Sources:** [Other places document can be found]
- **Future Monitoring:** [Any concerns about URL stability]
- **Special Requirements:** [Access restrictions, file size, etc.]

---

### Approval Checklist

- [ ] New URL tested manually in browser
- [ ] PDF downloads and opens correctly
- [ ] Content matches expected grade levels
- [ ] URL is from official state education source
- [ ] No authentication or paywall required
- [ ] File size reasonable (< 50 MB)
- [ ] states.json backup created before update
