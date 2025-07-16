<script lang="ts">
  import type { Project } from "$lib/types/tool";

  export let projects: Project[] = [];
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
          {#each projects as project}
            <tr>
              <td>{project.name}</td>
              <td>{project.description}</td>
              <td>
                <a href={`/tools/projects/${project.id}`} class="btn btn-xs btn-ghost">Opties</a>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if projects.length === 0}
        <div class="py-12 text-center opacity-70">Geen projecten gevonden.</div>
      {/if}
    </div>
  </div>
</div>