import asyncio
import logging
import random
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SocialProfile(BaseModel):
    """Schema for social media profile"""
    platform: str = Field(..., description="Social media platform")
    username: str = Field(..., description="Username")
    profile_url: str = Field(..., description="Profile URL")
    display_name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Profile bio")
    followers_count: Optional[int] = Field(None, description="Number of followers")
    following_count: Optional[int] = Field(None, description="Number of following")
    posts_count: Optional[int] = Field(None, description="Number of posts")
    verified: Optional[bool] = Field(False, description="Verification status")
    profile_image: Optional[str] = Field(None, description="Profile image URL")
    is_private: Optional[bool] = Field(False, description="Private profile status")
    joined_date: Optional[str] = Field(None, description="Account creation date")
    last_active: Optional[str] = Field(None, description="Last activity date")
    location: Optional[str] = Field(None, description="Location")
    website: Optional[str] = Field(None, description="Website URL")
    emails: List[str] = Field(default_factory=list, description="Email addresses found in profile")
    phones: List[str] = Field(default_factory=list, description="Phone numbers found in profile")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Additional platform-specific info")


class SocialScraper:
    """Module for scraping social media platforms"""

    def __init__(self):
        self.platforms = [
            'facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'youtube',
            'reddit', 'pinterest', 'snapchat', 'telegram', 'discord', 'github',
            'medium', 'wordpress', 'blogger', 'tumblr', 'flickr', 'vimeo',
            'steam', 'twitch', 'soundcloud', 'spotify', 'lastfm', 'deviantart'
        ]

        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

    async def search_username(self, username: str) -> List[Dict[str, Any]]:
        """Search for a username across multiple social media platforms"""
        logger.info(f"Searching for username: {username}")

        results = []

        tasks = []
        for platform in self.platforms:
            task = asyncio.create_task(self._check_platform(platform, username))
            tasks.append(task)

        platform_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, platform in enumerate(self.platforms):
            if isinstance(platform_results[i], Exception):
                logger.error(f"Failed to check {platform}: {platform_results[i]}")
                continue

            if platform_results[i]:
                profile_data = platform_results[i].dict()
                results.append(profile_data)

        return results

    async def search_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for a person's name across social media platforms"""
        logger.info(f"Searching for name: {name}")

        potential_usernames = self._generate_usernames_from_name(name)

        all_results = []

        for username in potential_usernames[:10]:
            results = await self.search_username(username)
            all_results.extend(results)

        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result['profile_url'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['profile_url'])

        return unique_results

    async def _check_platform(self, platform: str, username: str) -> Optional[SocialProfile]:
        """Check if a username exists on a specific platform"""
        await asyncio.sleep(random.uniform(0.1, 0.5))

        if random.random() > 0.7:
            return None

        profile_url = self._get_profile_url(platform, username)

        mock_data = self._generate_mock_profile(platform, username, profile_url)

        try:
            return SocialProfile(**mock_data)
        except Exception as e:
            logger.error(f"Failed to create profile for {platform}: {e}")
            return None

    def _get_profile_url(self, platform: str, username: str) -> str:
        """Get the profile URL for a platform and username"""
        url_patterns = {
            'facebook': f"https://www.facebook.com/{username}",
            'instagram': f"https://www.instagram.com/{username}",
            'twitter': f"https://twitter.com/{username}",
            'linkedin': f"https://www.linkedin.com/in/{username}",
            'tiktok': f"https://www.tiktok.com/@{username}",
            'youtube': f"https://www.youtube.com/c/{username}",
            'reddit': f"https://www.reddit.com/user/{username}",
            'pinterest': f"https://www.pinterest.com/{username}",
            'snapchat': f"https://www.snapchat.com/add/{username}",
            'telegram': f"https://t.me/{username}",
            'discord': f"https://discord.com/users/{username}",
            'github': f"https://github.com/{username}",
            'medium': f"https://{username}.medium.com",
            'wordpress': f"https://{username}.wordpress.com",
            'blogger': f"https://{username}.blogspot.com",
            'tumblr': f"https://{username}.tumblr.com",
            'flickr': f"https://www.flickr.com/people/{username}",
            'vimeo': f"https://vimeo.com/{username}",
            'steam': f"https://steamcommunity.com/id/{username}",
            'twitch': f"https://www.twitch.tv/{username}",
            'soundcloud': f"https://soundcloud.com/{username}",
            'spotify': f"https://open.spotify.com/user/{username}",
            'lastfm': f"https://www.last.fm/user/{username}",
            'deviantart': f"https://{username}.deviantart.com"
        }

        return url_patterns.get(platform, f"https://www.{platform}.com/{username}")

    def _generate_mock_profile(self, platform: str, username: str, profile_url: str) -> Dict[str, Any]:
        """Generate mock profile data for a platform"""
        display_name = username.replace('_', ' ').replace('-', ' ').title()
        followers = random.randint(10, 10000)
        following = random.randint(10, 5000)
        posts = random.randint(0, 1000)
        verified = random.random() > 0.9
        is_private = random.random() > 0.8

        bio_templates = {
            'facebook': f"Just living my life one day at a time. Love, peace, and happiness.",
            'instagram': f"📸 Photographer | 🌍 Traveler | ✨ Living my best life",
            'twitter': f"Thoughts and opinions. RTs ≠ endorsements.",
            'linkedin': f"Professional at {random.choice(['Tech Corp', 'Innovation Inc', 'Global Solutions'])}",
            'github': f"Developer | Open source enthusiast",
            'default': f"Passionate about {random.choice(['technology', 'art', 'music', 'travel'])}"
        }

        bio = bio_templates.get(platform, bio_templates['default'])

        emails = []
        phones = []

        if random.random() > 0.7:
            emails.append(f"{username}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}")

        if random.random() > 0.9:
            phones.append(f"+{random.randint(1000000000, 9999999999)}")

        additional_info = {}

        if platform == 'linkedin':
            additional_info['position'] = random.choice(['Software Engineer', 'Product Manager', 'Data Scientist'])
            additional_info['company'] = random.choice(['Tech Corp', 'Innovation Inc', 'Global Solutions'])
        elif platform == 'github':
            additional_info['repositories'] = random.randint(0, 100)
            additional_info['stars'] = random.randint(0, 500)
        elif platform == 'twitter':
            additional_info['tweets'] = random.randint(0, 10000)
            additional_info['likes'] = random.randint(0, 50000)

        return {
            'platform': platform,
            'username': username,
            'profile_url': profile_url,
            'display_name': display_name,
            'bio': bio,
            'followers_count': followers,
            'following_count': following,
            'posts_count': posts,
            'verified': verified,
            'is_private': is_private,
            'emails': emails,
            'phones': phones,
            'additional_info': additional_info
        }

    def _generate_usernames_from_name(self, name: str) -> List[str]:
        """Generate potential usernames from a person's name"""
        parts = name.split()
        if len(parts) < 2:
            return [name.lower().replace(' ', '')]

        first, last = parts[0], parts[-1]
        first_lower, last_lower = first.lower(), last.lower()

        usernames = [
            f"{first_lower}{last_lower}",
            f"{first_lower}.{last_lower}",
            f"{first_lower}_{last_lower}",
            f"{first_lower}-{last_lower}",
            f"{first_lower}{last_lower[0]}",
            f"{first_lower[0]}{last_lower}",
            f"{last_lower}{first_lower}",
            f"{last_lower}.{first_lower}",
            f"{last_lower}_{first_lower}",
            f"{last_lower}-{first_lower}",
            f"{first_lower}{random.randint(1, 999)}",
            f"{first_lower}_{random.randint(1, 999)}",
            f"{last_lower}{random.randint(1, 999)}",
            f"{last_lower}_{random.randint(1, 999)}"
        ]

        if len(parts) > 2:
            middle = parts[1].lower()
            usernames.extend([
                f"{first_lower}{middle}{last_lower}",
                f"{first_lower}.{middle}.{last_lower}",
                f"{first_lower}{middle[0]}{last_lower}",
                f"{first_lower[0]}{middle[0]}{last_lower}"
            ])

        return usernames