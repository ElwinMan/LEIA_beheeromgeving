<script lang="ts">
  import type { Story } from '$lib/types/tool';

  export let stories: Story[] = [];
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 font-bold">Naam</th>
            <th class="bg-base-200 font-bold">Beschrijving</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each stories as story}
            <tr>
              <td>{story.name}</td>
              <td>{story.description}</td>
              <td>
                <a href={`/tools/stories/${story.id}`} class="btn btn-xs btn-ghost">Opties</a>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if stories.length === 0}
        <div class="py-12 text-center opacity-70">Geen stories gevonden.</div>
      {/if}
    </div>
  </div>
</div>