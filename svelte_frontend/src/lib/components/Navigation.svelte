<script lang="ts">
  import { page } from '$app/stores';
  interface Props {
    children?: import('svelte').Snippet;
  }

  let { children }: Props = $props();

  const navigationItems = [
    { href: '/digital-twins', label: 'Digital Twins', icon: '/icons/database.svg' },
    { href: '/background-layers', label: 'Background Layers', icon: '/icons/layers.svg' },
    { href: '/feature-layers', label: 'Feature Layers', icon: '/icons/layers.svg' },
    {
      href: '/tools',
      label: 'Tools',
      icon: '/icons/wrench.svg',
      children: [
        { href: '/tools/projects', label: 'Projects' },
        { href: '/tools/bookmarks', label: 'Bookmarks' },
        { href: '/tools/terrain-providers', label: 'Terrain Providers' },
        { href: '/tools/stories', label: 'Stories' }
      ]
    }
  ];

  function isActive(href: string) {
    return $page.url.pathname === href;
  }
</script>

<div class="drawer lg:drawer-open">
  <input id="drawer-toggle" type="checkbox" class="drawer-toggle" />

  <div class="drawer-content flex flex-col">
    <!-- Navbar for mobile -->
    <div class="navbar bg-base-100 lg:hidden">
      <div class="flex-none">
        <label for="drawer-toggle" class="btn btn-square btn-ghost">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            ></path>
          </svg>
        </label>
      </div>
      <div class="flex-1">
        <span class="text-xl font-bold">LEIA Beheeromgeving</span>
      </div>
    </div>

    <!-- Page content slot -->
    <main class="flex-1 p-6">
      {@render children?.()}
    </main>
  </div>

  <div class="drawer-side">
    <label for="drawer-toggle" aria-label="close sidebar" class="drawer-overlay"></label>
    <aside class="bg-base-200 min-h-full w-80">
      <div class="p-4">
        <h1 class="mb-8 hidden text-xl font-bold lg:block">LEIA Beheeromgeving</h1>

        <ul class="menu space-y-2 p-0">
          {#each navigationItems as item}
            <li>
              <a
                href={item.href}
                class="flex items-center gap-3 {isActive(item.href) ? 'active' : ''}"
              >
                <img src={item.icon} alt={item.label} class="h-5 w-5" />
                {item.label}
              </a>
              {#if item.children}
                <ul class="ml-4 mt-2 space-y-2">
                  {#each item.children as child}
                    <li>
                      <a
                        href={child.href}
                        class="flex items-center gap-3 {isActive(child.href) ? 'active' : ''}"
                      >
                        <span class="text-sm">{child.label}</span>
                      </a>
                    </li>
                  {/each}
                </ul>
              {/if}
            </li>
          {/each}
        </ul>
      </div>
    </aside>
  </div>
</div>
