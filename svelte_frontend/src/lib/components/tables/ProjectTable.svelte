<script lang="ts">
  import type { Project } from "$lib/types/tool";
  import UpdateProjectModal from "$lib/components/modals/UpdateProjectModal.svelte";
  import { deleteProject } from "$lib/api";

  export let projects: Project[] = [];

  let modalComponent: any;

  function handleOpenModal(project: Project) {
    modalComponent.showModal(project);
  }

  async function handleDelete(projectId: number) {
    if (confirm('Weet je zeker dat je dit project wilt verwijderen?')) {
      try {
        await deleteProject(String(projectId));
        projects = projects.filter(p => p.id !== projectId);
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleUpdated(event: CustomEvent<Project>) {
    const updatedProject = event.detail;
    const idx = projects.findIndex(p => p.id === updatedProject.id);
    if (idx > -1) {
      projects[idx] = updatedProject;
      projects = [...projects];
    }
  }
</script>

<UpdateProjectModal bind:this={modalComponent} on:updated={handleUpdated} />

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
              <td class="relative">
                <details class="dropdown dropdown-end">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-40 p-2 shadow">
                    <li>
                      <button on:click={() => handleOpenModal(project)} class="flex items-center gap-2">
                        Bewerken
                      </button>
                    </li>
                    <li>
                      <button class="text-error" on:click={() => handleDelete(project.id)}>
                        Verwijderen
                      </button>
                    </li>
                  </ul>
                </details>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      
      <!-- Add padding at the bottom for dropdown space -->
      <!-- Temp fix till dropdown fix for absolute position -->
      <div class="h-32"></div>

      {#if projects.length === 0}
        <div class="py-12 text-center opacity-70">Geen projecten gevonden.</div>
      {/if}
    </div>
  </div>
</div>