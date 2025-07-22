<script lang="ts">
  export let digitalTwinsForLayer: Array<{ id: number; name: string; title?: string }> = [];
  export let selectedLayerTitle: string = '';
  let modalRef: any;
  export function showModal() { modalRef.showModal(); }
</script>

<dialog bind:this={modalRef} class="modal">
  <div class="modal-box max-w-xl">
    <h3 class="font-bold text-lg mb-2">
      Digital Twins voor layer: <span class="text-base-content/70">{selectedLayerTitle}</span>
    </h3>
    <div class="mb-4 text-sm text-base-content">
      {digitalTwinsForLayer.length} digital twin{digitalTwinsForLayer.length === 1 ? '' : 's'} gebruiken deze layer
    </div>
    {#if digitalTwinsForLayer.length > 0}
      <ul class="space-y-2">
        {#each digitalTwinsForLayer as twin}
          <li class="flex items-center gap-2">
            <span class="inline-block h-2 w-2 rounded-full bg-blue-500"></span>
            <a
              href={`/digital-twins/${twin.id}`}
              class="font-medium link link-neutral"
              target="_blank"
              rel="noopener noreferrer"
              title="Open digital twin"
            >
              {twin.title}
            </a>
            <span class="text-xs text-base-content/90">{twin.name}</span>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-base-content/60">Geen digital twins gebruiken deze layer.</p>
    {/if}
    <form method="dialog" class="mt-6">
      <button class="btn btn-sm btn-primary">Sluiten</button>
    </form>
  </div>
</dialog>