<script lang="ts">
  import { onMount } from 'svelte';
  import StoryTable from '$lib/components/tables/StoryTable.svelte';
  import type { Story } from '$lib/types/tool';

  interface Data {
    stories: Story[];
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
  <title>LEIA Beheeromgeving – Stories</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold">Stories</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle stories</p>
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
    <StoryTable stories={data.stories} />
  {/if}
</div>