export interface Server {
    id: string;
    label: string;
    color: string;
}

export interface TextChannel {
    id: string;
    name: string;
    unread?: boolean;
}

export interface VoiceChannel {
    id: string;
    name: string;
    active?: boolean;
}

export type UserStatus = "online" | "away" | "offline";

export interface Message {
    id: number | string;
    author: string;
    initials: string;
    color: string;
    time: string;
    text: string;
    quoted?: boolean;
}

export interface Member {
    name: string;
    initials: string;
    color: string;
    status: UserStatus;
}
