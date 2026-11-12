#!/usr/bin/env python3
"""引用质量查询：输入 DOI 或标题（每行一个，可带 "ID<TAB>" 前缀），输出 CSV。
用法: python3 openalex_lookup.py refs.txt > out.csv
字段: id, query, title, year, type, venue, issn, cited_by, cites_per_year, venue_h_index, venue_2yr_citedness, openalex_id
分区（JCR/中科院/SJR）和中文核心目录 OpenAlex 不提供，需另查。
"""
import sys, csv, json, time, datetime, urllib.parse, urllib.request

UA = {"User-Agent": "citation-quality-audit (OpenAlex polite pool: set your email)"}
YEAR = datetime.date.today().year
_src_cache = {}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def find_work(q):
    q = q.strip()
    if q.lower().startswith("10.") or "doi.org/" in q:
        doi = q.split("doi.org/")[-1]
        try:
            return get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/"))
        except Exception:
            return None
    try:
        res = get("https://api.openalex.org/works?per_page=1&search=" + urllib.parse.quote(q))
        return res["results"][0] if res.get("results") else None
    except Exception:
        return None

def source_stats(sid):
    if not sid:
        return None, None
    if sid not in _src_cache:
        try:
            s = get("https://api.openalex.org/sources/" + sid.split("/")[-1])
            st = s.get("summary_stats") or {}
            _src_cache[sid] = (st.get("h_index"), round(st.get("2yr_mean_citedness") or 0, 2))
        except Exception:
            _src_cache[sid] = (None, None)
    return _src_cache[sid]

def ai(wk):
    out = []
    for a in (wk.get("authorships") or [])[:4]:
        inst = "/".join(i.get("display_name","") for i in (a.get("institutions") or [])[:1])
        out.append(f'{(a.get("author") or {}).get("display_name","")}({inst})')
    return "; ".join(out)

def main():
    w = csv.writer(sys.stdout)
    w.writerow(["id", "query", "title", "year", "type", "venue", "issn", "cited_by",
                "cites_per_year", "venue_h_index", "venue_2yr_citedness", "authors_institutions", "openalex_id"])
    for line in open(sys.argv[1], encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        rid, q = (line.split("\t", 1) if "\t" in line else ("", line))
        wk = find_work(q)
        if not wk:
            w.writerow([rid, q, "NOT FOUND"] + [""] * 10)
            continue
        src = (wk.get("primary_location") or {}).get("source") or {}
        h, c2 = source_stats(src.get("id"))
        y = wk.get("publication_year") or YEAR
        cites = wk.get("cited_by_count") or 0
        w.writerow([rid, q, wk.get("title"), y, wk.get("type"), src.get("display_name"),
                    src.get("issn_l"), cites, round(cites / max(1, YEAR - y + 1), 1), h, c2, ai(wk), wk.get("id")])
        time.sleep(0.2)

if __name__ == "__main__":
    main()
