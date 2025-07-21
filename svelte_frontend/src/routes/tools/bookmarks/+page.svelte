<script lang="ts">
  import { onMount } from 'svelte';
  import BookmarkTable from '$lib/components/tables/BookmarkTable.svelte';
  import CreateBookmarkModal from '$lib/components/modals/CreateBookmarkModal.svelte';
  import { fetchBookmarks } from '$lib/api';
  import type { Bookmark } from '$lib/types/tool';

  interface Data {
    bookmarks: Bookmark[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);
  let createModal: any;

  async function reloadBookmarks() {
    isLoading = true;
    try {
      data.bookmarks = await fetchBookmarks();
    } catch (e) {
      data.error = 'Kon bookmarks niet laden';
    } finally {
      isLoading = false;
    }
  }

  onMount(reloadBookmarks);
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Bookmarks</title>
</svelte:head>

<div class="space-y-6">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h1 class="text-3xl font-bold">Bookmarks</h1>
      <p class="text-base-content/70 mt-2">Beheer en bekijk alle bookmarks</p>
    </div>
    <button class="btn btn-primary" onclick={() => createModal.showModal()}>
      Nieuwe Bookmark
    </button>
  </div>

  <CreateBookmarkModal bind:this={createModal} on:created={reloadBookmarks} />

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