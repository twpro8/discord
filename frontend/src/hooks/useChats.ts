import { useInfiniteQuery } from "@tanstack/react-query";
import { chatsGetMyChatsInfiniteOptions } from "@/client/@tanstack/react-query.gen";

export function useChats() {
    const query = useInfiniteQuery({
        ...chatsGetMyChatsInfiniteOptions({ query: { limit: 10 } }),
        getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
    });

    const items = query.data?.pages.flatMap((page) => page.items) ?? [];

    return {
        items,
        isLoading: query.isLoading,
        error: query.error?.detail ?? null,
        hasMore: query.hasNextPage ?? false,
        loadMore: query.fetchNextPage,
    };
}
