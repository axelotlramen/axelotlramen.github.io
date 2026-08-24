import { PlaySquare, X as XIcon } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { profile } from "@/content/profile";

export function IntroCard() {
  return (
    <div
      className="relative rounded-sm border border-border bg-card p-6 shadow-[4px_6px_0_rgba(0,0,0,0.12)] transition-transform duration-150 hover:rotate-0"
      style={{ transform: "rotate(-1deg)" }}
    >
      <div
        className="absolute -top-3 left-10 h-6 w-20 -rotate-3 opacity-80"
        style={{ backgroundColor: "var(--tab-home)" }}
      />

      <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
        <div className="flex items-center gap-4 sm:w-64 sm:shrink-0">
          <Avatar className="size-20 border-2 border-card shadow-md">
            <AvatarImage src={profile.avatarUrl} alt={profile.username} referrerPolicy="no-referrer" />
            <AvatarFallback>{profile.username.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <div className="text-3xl leading-tight" style={{ fontFamily: "var(--font-heading)" }}>
              {profile.username}
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <a
                href={profile.youtubeUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium text-white"
                style={{ backgroundColor: "var(--tab-hsr)" }}
              >
                <PlaySquare className="size-3.5" />
                YouTube
              </a>
              <a
                href={profile.twitterUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
                style={{ backgroundColor: "var(--ink)", color: "var(--card)" }}
              >
                <XIcon className="size-3.5" />
                Twitter
              </a>
            </div>
          </div>
        </div>

        <p className="flex-1 text-sm text-muted-foreground">{profile.bio}</p>
      </div>

      {profile.latestVideoId && (
        <div className="mt-5 aspect-video w-full overflow-hidden rounded-md border border-border">
          <iframe
            className="h-full w-full"
            src={`https://www.youtube.com/embed/${profile.latestVideoId}`}
            title="Latest video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}
    </div>
  );
}
