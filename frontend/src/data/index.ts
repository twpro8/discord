import type { Server, TextChannel, VoiceChannel, ChatEntry, Message, Member } from "@/types";

export const SERVERS: Server[] = [
    { id: "lumiere", label: "✦", color: "var(--mauve)", shape: "rounded" },
    { id: "design",  label: "◆", color: "var(--red)", shape: "rounded" },
    { id: "dev",     label: "▲", color: "var(--green)",    shape: "rounded" },
];

export const TEXT_CHANNELS: TextChannel[] = [
    { id: "general",       name: "general",       unread: true },
    { id: "design",        name: "design"                      },
    { id: "backend",       name: "backend"                     },
    { id: "random",        name: "random"                      },
    { id: "announcements", name: "announcements"               },
];

export const VOICE_CHANNELS: VoiceChannel[] = [
    { id: "lounge",      name: "Lounge",      active: true },
    { id: "design-room", name: "Design room"               },
    { id: "team-only",   name: "Team only"                 },
];

export const SERVER_MEMBERS: Member[] = [
    { name: "Alice",  initials: "AL", color: "var(--blue)",     status: "online"  },
    { name: "Blake",  initials: "BL", color: "var(--flamingo)", status: "online"  },
    { name: "Priya",  initials: "PR", color: "var(--green)",    status: "online"  },
    { name: "Sam",    initials: "SC", color: "var(--mauve)",    status: "online"  },
    { name: "Jordan", initials: "JO", color: "var(--overlay1)", status: "away"    },
    { name: "Casey",  initials: "CA", color: "var(--overlay1)", status: "away"    },
    { name: "Taylor", initials: "TA", color: "var(--overlay1)", status: "away"    },
];

export const SERVER_MESSAGES: Record<string, Message[]> = {
    general: [
        { id: 1, author: "Alice",  initials: "AL", color: "var(--blue)",     time: "10:32 AM", text: "Hey everyone! Just pushed the new UI changes to the repo." },
        { id: 2, author: "Blake",  initials: "BL", color: "var(--flamingo)", time: "10:45 AM", text: "Looks great! Will review by noon." },
        { id: 3, author: "Priya",  initials: "PR", color: "var(--green)",    time: "10:51 AM", text: "API changes are deployed to staging ✓" },
        { id: 4, author: "Sam",    initials: "SC", color: "var(--mauve)",    time: "11:02 AM", text: "Anyone joining standup?" },
    ],
    design: [
        { id: 1, author: "Blake",  initials: "BL", color: "var(--flamingo)", time: "9:15 AM",  text: "Uploaded the new Figma mockups, check the link in pinned." },
        { id: 2, author: "Alice",  initials: "AL", color: "var(--blue)",     time: "9:22 AM",  text: "The color palette looks much better in v3." },
        { id: 3, author: "Taylor", initials: "TA", color: "var(--overlay1)", time: "9:40 AM",  text: "Can we revisit the typography on mobile? Feels cramped." },
        { id: 4, author: "Blake",  initials: "BL", color: "var(--flamingo)", time: "9:44 AM",  text: "Good call, I'll open a ticket." },
    ],
    backend: [
        { id: 1, author: "Priya",  initials: "PR", color: "var(--green)",    time: "8:50 AM",  text: "Postgres migration ran clean on staging." },
        { id: 2, author: "Jordan", initials: "JO", color: "var(--yellow)",   time: "9:03 AM",  text: "Nice. What's the rollback plan if prod fails?" },
        { id: 3, author: "Priya",  initials: "PR", color: "var(--green)",    time: "9:07 AM",  text: "We keep the old schema for 48h, documented in the runbook." },
        { id: 4, author: "Sam",    initials: "SC", color: "var(--mauve)",    time: "9:20 AM",  text: "Approved. Let's schedule prod for Thursday." },
    ],
    random: [
        { id: 1, author: "Casey",  initials: "CA", color: "var(--sky)",      time: "11:30 AM", text: "Anyone else think the office coffee got worse?" },
        { id: 2, author: "Jordan", initials: "JO", color: "var(--yellow)",   time: "11:31 AM", text: "It was never good 😂" },
        { id: 3, author: "Alice",  initials: "AL", color: "var(--blue)",     time: "11:35 AM", text: "I just bring my own at this point." },
        { id: 4, author: "Taylor", initials: "TA", color: "var(--overlay1)", time: "11:38 AM", text: "French press gang rise up ☕" },
    ],
    announcements: [
        { id: 1, author: "Sam",    initials: "SC", color: "var(--mauve)",    time: "Mon 9:00 AM", text: "Sprint 14 kicks off today. Goals are in Notion." },
        { id: 2, author: "Sam",    initials: "SC", color: "var(--mauve)",    time: "Mon 9:01 AM", text: "Reminder: retro is Friday at 4pm, attendance required." },
        { id: 3, author: "Alice",  initials: "AL", color: "var(--blue)",     time: "Tue 10:00 AM", text: "New design system docs are live at design.lumiere.dev 🎉" },
    ],
};

export const GROUP_CHATS: ChatEntry[] = [
    {
        id: "g1", name: "Design team",    initials: "DT", color: "var(--mauve)",
        lastMessage: "Priya: Looks good to me!", time: "11:02", unread: 3, isGroup: true,
        members: ["AL", "BL", "PR", "SC"],
    },
    {
        id: "g2", name: "Frontend squad", initials: "FS", color: "var(--peach)",
        lastMessage: "You: PR is up for review", time: "10:44", unread: 0, isGroup: true,
        members: ["AL", "JO", "TA"],
    },
    {
        id: "g3", name: "Standup",        initials: "ST", color: "var(--teal)",
        lastMessage: "Sam: Anyone joining?", time: "Yesterday", unread: 0, isGroup: true,
        members: ["BL", "PR", "SC", "CA"],
    },
];

export const DIRECT_CHATS: ChatEntry[] = [
    { id: "d1", name: "Alice",  initials: "AL", color: "var(--blue)",     lastMessage: "Just pushed the new UI changes", time: "10:32",    unread: 1, isGroup: false, status: "online"  },
    { id: "d2", name: "Blake",  initials: "BL", color: "var(--flamingo)", lastMessage: "Will review by noon.",           time: "10:45",    unread: 0, isGroup: false, status: "online"  },
    { id: "d3", name: "Priya",  initials: "PR", color: "var(--green)",    lastMessage: "API changes are deployed ✓",    time: "10:51",    unread: 0, isGroup: false, status: "online"  },
    { id: "d4", name: "Sam",    initials: "SC", color: "var(--mauve)",    lastMessage: "Anyone joining standup?",        time: "11:02",    unread: 0, isGroup: false, status: "away"    },
    { id: "d5", name: "Jordan", initials: "JO", color: "var(--yellow)",   lastMessage: "See you tomorrow!",             time: "Yesterday", unread: 0, isGroup: false, status: "away"    },
    { id: "d6", name: "Casey",  initials: "CA", color: "var(--sky)",      lastMessage: "Sounds great 👍",               time: "Monday",   unread: 0, isGroup: false, status: "offline" },
];

export const DM_MESSAGES: Record<string, Message[]> = {
    g1: [
        { id: 1, author: "Alice", initials: "AL", color: "var(--blue)",     time: "10:15 AM", text: "Morning everyone! Ready for the design review?" },
        { id: 2, author: "Blake", initials: "BL", color: "var(--flamingo)", time: "10:17 AM", text: "Yes! Just finishing up the mockups." },
        { id: 3, author: "Priya", initials: "PR", color: "var(--green)",    time: "10:22 AM", text: "Looks good to me!" },
    ],
    g2: [
        { id: 1, author: "Alice", initials: "AL", color: "var(--blue)",  time: "10:40 AM", text: "Frontend build is passing ✓" },
        { id: 2, author: "You",   initials: "YO", color: "var(--peach)", time: "10:44 AM", text: "PR is up for review" },
    ],
    g3: [
        { id: 1, author: "Sam", initials: "SC", color: "var(--mauve)", time: "Yesterday", text: "Anyone joining standup?" },
    ],
    d1: [
        { id: 1, author: "Alice", initials: "AL", color: "var(--blue)",  time: "10:30 AM", text: "Hey! Do you have a minute?" },
        { id: 2, author: "You",   initials: "YO", color: "var(--peach)", time: "10:31 AM", text: "Sure, what's up?" },
        { id: 3, author: "Alice", initials: "AL", color: "var(--blue)",  time: "10:32 AM", text: "Just pushed the new UI changes to the repo." },
    ],
    d2: [{ id: 1, author: "Blake",  initials: "BL", color: "var(--flamingo)", time: "10:45 AM",  text: "Will review by noon." }],
    d3: [{ id: 1, author: "Priya",  initials: "PR", color: "var(--green)",    time: "10:51 AM",  text: "API changes are deployed to staging ✓" }],
    d4: [{ id: 1, author: "Sam",    initials: "SC", color: "var(--mauve)",    time: "11:02 AM",  text: "Anyone joining standup?" }],
    d5: [{ id: 1, author: "Jordan", initials: "JO", color: "var(--yellow)",   time: "Yesterday", text: "See you tomorrow!" }],
    d6: [{ id: 1, author: "Casey",  initials: "CA", color: "var(--sky)",      time: "Monday",    text: "Sounds great 👍" }],
};
