"""GitHub stats extractor."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any
import httpx
import re
from app.core.config import settings
from app.core.errors import AppError, ErrorCode

__all__ = ["GitHubProfile", "parse_github_data", "fetch_and_normalize_github"]

async def fetch_and_normalize_github(profile_url: str) -> dict[str, Any]:
    """Fetch GitHub profile and repositories via REST API."""
    match = re.search(r"github\.com/([^/]+)", profile_url)
    if not match:
        raise AppError(status_code=400, code=ErrorCode.VALIDATION_ERROR, message="invalid_github_url")
    
    username = match.group(1)
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if settings.github_pat and settings.github_pat.get_secret_value():
        headers["Authorization"] = f"token {settings.github_pat.get_secret_value()}"
        
    async with httpx.AsyncClient() as client:
        # Fetch user
        user_res = await client.get(f"https://api.github.com/users/{username}", headers=headers)
        if user_res.status_code != 200:
            raise AppError(status_code=400, code=ErrorCode.VALIDATION_ERROR, message=f"GitHub API Error: {user_res.status_code}")
        
        user_data = user_res.json()
        
        # Fetch repos
        repos_res = await client.get(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated", headers=headers)
        repos_data = repos_res.json() if repos_res.status_code == 200 else []
        
        # Aggregate languages
        languages = {}
        processed_repos = []
        for repo in repos_data:
            if repo.get("fork"): continue
            
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
                
            processed_repos.append({
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": lang,
                "stars": repo.get("stargazers_count", 0),
                "topics": repo.get("topics", [])
            })
            
        return {
            "username": user_data.get("login"),
            "total_commits": user_data.get("public_repos", 0) * 10,  # Proxy for commits in MVP
            "total_stars": sum(r["stars"] for r in processed_repos),
            "languages": languages,
            "repos": processed_repos
        }

@dataclass
@dataclass
class GitHubProfile:
    username: str
    repos: list[dict[str, Any]]
    total_commits: int
    total_stars: int
    languages: dict[str, int]

async def parse_github_data(raw: dict[str, Any]) -> tuple[str, uuid.UUID]:
    """Extract and flatten GitHub data into structured text."""
    parts = []
    username = raw.get("username", "Unknown")
    parts.append(f"GitHub Profile: {username}")
    parts.append(f"Total Commits: {raw.get('total_commits', 0)}")
    parts.append(f"Total Stars: {raw.get('total_stars', 0)}")
    
    languages = raw.get("languages", {})
    if languages:
        langs_str = ", ".join(f"{lang} ({bytes_cnt} bytes)" for lang, bytes_cnt in languages.items())
        parts.append(f"Languages: {langs_str}")
    
    repos = raw.get("repos", [])
    if repos:
        parts.append("Repositories:")
        for repo in repos:
            name = repo.get("name", "Unknown")
            desc = repo.get("description", "")
            lang = repo.get("language", "")
            stars = repo.get("stars", 0)
            topics = repo.get("topics", [])
            
            repo_str = f"- {name}"
            if desc:
                repo_str += f": {desc}"
            if lang:
                repo_str += f" [{lang}]"
            repo_str += f" (Stars: {stars})"
            if topics:
                repo_str += f" Topics: {', '.join(topics)}"
            parts.append(repo_str)
            
    structured_text = "\n".join(parts)
    document_id = uuid.uuid4()
    return structured_text, document_id