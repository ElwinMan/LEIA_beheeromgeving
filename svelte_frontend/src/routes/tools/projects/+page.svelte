<script lang="ts">
  import { onMount } from 'svelte';
  import ProjectTable from '$lib/components/tables/ProjectTable.svelte';
  import type { Project } from '$lib/types/tool';

  interface Data {
    projects: Project[];
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
  <title>LEIA Beheeromgeving – Projects</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold">Projects</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle projecten</p>
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
    <ProjectTable projects={data.projects} />
  {/if}
</div>