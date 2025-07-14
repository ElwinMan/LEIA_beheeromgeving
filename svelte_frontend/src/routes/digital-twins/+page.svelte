<script lang="ts">
  import { onMount } from 'svelte';
  import DigitalTwinTable from '$lib/components/tables/DigitalTwinTable.svelte';
  import CreateDigitalTwinModal from '$lib/components/modals/CreateDigitalTwinModal.svelte';

  let { data } = $props();
  let isLoading = $state(true);

  let digitalTwinModalRef: InstanceType<typeof CreateDigitalTwinModal>;

  function refresh() {
    // Optionally re-fetch the data
    location.reload(); // or call your fetch function
  }

  onMount(() => {
    setTimeout(() => {
      isLoading = false;
    }, 100);
  });
</script>

<svelte:head>
  <title>LEIA Beheeromgeving</title>
</svelte:head>

<CreateDigitalTwinModal
  bind:this={digitalTwinModalRef}
  on:created={refresh}
/>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold">Digital Twins</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle beschikbare digital twins</p>

    <button
      class="btn btn-sm btn-outline mb-2"
      onclick={() => digitalTwinModalRef.showModal()}
    >
      <img src="/icons/plus.svg" alt="Nieuwe twin" class="mr-1 h-4 w-4" />
      Digital Twin aanmaken
    </button>
  </div>

  {#if isLoading}
    <div class="flex items-center justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
      <span class="ml-3">Laden...</span>
    </div>
  {:else if data.error}
    <div class="alert alert-error">Fout: {data.error}</div>
  {:else}
    <DigitalTwinTable digitalTwins={data.digitalTwins} />
  {/if}
</div>