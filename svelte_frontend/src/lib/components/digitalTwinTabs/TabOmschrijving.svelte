<script lang="ts">
  import type { DigitalTwin } from '$lib/types/digitalTwin';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();
</script>

<div class="space-y-6">
  <h2 class="text-2xl font-bold">Omschrijving</h2>
  <p class="text-base-content/70">Algemene informatie over deze digital twin.</p>
  
  {#if digitalTwin}
    <div class="card bg-base-100 border border-base-300">
      <div class="card-body">
        <h3 class="card-title">{digitalTwin.title}</h3>
        <p><strong>Naam:</strong> {digitalTwin.name}</p>
        <p><strong>Subtitle:</strong> {digitalTwin.subtitle}</p>
        <p><strong>Eigenaar:</strong> {digitalTwin.owner}</p>
        <p><strong>Laatst gewijzigd:</strong> {digitalTwin.last_updated}</p>
        <p><strong>Privé:</strong> {digitalTwin.private ? 'Ja' : 'Nee'}</p>
      </div>
    </div>
  {:else}
    <p>Geen data beschikbaar voor digital twin ID: {digitalTwinId}</p>
  {/if}
</div>
