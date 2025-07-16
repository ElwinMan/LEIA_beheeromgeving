<script lang="ts">
  import type { Bookmark } from "$lib/types/tool";

  export let bookmarks: Bookmark[] = [];
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 font-bold">Titel</th>
            <th class="bg-base-200 font-bold">Beschrijving</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each bookmarks as bookmark}
            <tr>
              <td>{bookmark.title}</td>
              <td>{bookmark.description}</td>
              <td>
                <!-- Add your actions here -->
                <a href={`/tools/bookmarks/${bookmark.id}`} class="btn btn-xs btn-ghost">opties</a>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if bookmarks.length === 0}
        <div class="py-12 text-center opacity-70">Geen bookmarks gevonden.</div>
      {/if}
    </div>
  </div>
</div>