<template>
  <Navbar v-if="showNavbar" />
  <router-view />
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from './components/NavBar.vue';

const route = useRoute();

// 只在登入後顯示導覽列
const showNavbar = computed(() => route.path !== '/login' && route.path !== '/register');
</script>
