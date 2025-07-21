<script lang="ts">
  import { onMount } from 'svelte';
  import StoryTable from '$lib/components/tables/StoryTable.svelte';
  import CreateStoryModal from '$lib/components/modals/CreateStoryModal.svelte';
  import { fetchStories } from '$lib/api';
  import type { Story } from '$lib/types/tool';

  interface Data {
    stories: Story[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);
  let createModal: any;

  async function reloadStories() {
    isLoading = true;
    try {
      data.stories = await fetchStories();
    } catch (e) {
      data.error = 'Kon stories niet laden';
    } finally {
      isLoading = false;
    }
  }

  onMount(reloadStories);
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Stories</title>
</svelte:head>

<div class="space-y-6">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h1 class="text-3xl font-bold">Stories</h1>
      <p class="text-base-content/70 mt-2">Beheer en bekijk alle stories</p>
    </div>
    <button class="btn btn-primary" onclick={() => createModal.showModal()}>
      Nieuwe Story
    </button>
  </div>

  <CreateStoryModal bind:this={createModal} on:created={reloadStories} />

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
    <StoryTable stories={data.stories} />
  {/if}
</div>