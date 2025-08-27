<script lang="ts">
  export let missingFields: string[] = [];
</script>

{#if missingFields.length > 0}
  <div class="text-error mt-2 text-sm">
    Verplichte velden niet ingevuld: {missingFields.join(', ')}
  </div>
{/if}