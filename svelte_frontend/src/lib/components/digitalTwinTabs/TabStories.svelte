<script lang="ts">
  import type { DigitalTwin } from '$lib/types/digitalTwin';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();
</script>

<div class="space-y-6">
  <h2 class="text-2xl font-bold">Stories</h2>
  <p class="text-base-content/70">Beheer stories voor deze digital twin.</p>

  <div class="card bg-base-100 border-base-300 border">
    <div class="card-body">
      <p>Stories pagina is nog in ontwikkeling.</p>
      <p>Digital Twin ID: {digitalTwinId}</p>
    </div>
  </div>
</div>
