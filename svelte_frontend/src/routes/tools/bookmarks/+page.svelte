<script lang="ts">
  import { onMount } from 'svelte';
  import BookmarkTable from '$lib/components/tables/BookmarkTable.svelte';
  import type { Bookmark } from '$lib/types/tool';

  interface Data {
    bookmarks: Bookmark[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);

  onMount(() => {
    setTimeout(() => {
      isLoading = false;
    }, 100);
  });
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Bookmarks</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold">Bookmarks</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle bookmarks</p>
  </div>

  {#if isLoading}
    <div class="flex items-center justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
      <span class="ml-3">Laden...</span>
    </div>
  {:else if data.error}
    <div class="alert alert-error">
      <span>{data.error}</span>
    </div>
  {:else}
    <BookmarkTable bookmarks={data.bookmarks} />
  {/if}
</div>