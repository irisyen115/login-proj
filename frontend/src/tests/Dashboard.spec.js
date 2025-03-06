import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/DashboardView.vue';
import axios from 'axios';
import { nextTick } from 'vue';

jest.mock('axios'); // Mock Axios

describe('Dashboard.vue', () => {
  let wrapper;
  const mockRouter = createRouter({
    history: createWebHistory(),
    routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
  });

  beforeEach(async () => {
    localStorage.setItem('token', 'mock-token');
    sessionStorage.setItem('username', 'testuser');
    sessionStorage.setItem('lastLogin', '2024-03-01T12:00:00Z');
    sessionStorage.setItem('loginCount', '5');
    sessionStorage.setItem('role', 'admin');

    axios.get.mockResolvedValue({
      data: [
        { username: 'user1', last_login: '2024-03-02T14:00:00Z', login_count: 3, role: 'user' },
        { username: 'admin1', last_login: '2024-03-01T10:00:00Z', login_count: 10, role: 'admin' },
      ],
    });

    wrapper = mount(Dashboard, {
      global: {
        plugins: [mockRouter],
      },
    });

    await wrapper.vm.$nextTick();
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
  });

  it('應該正確渲染標題', () => {
    expect(wrapper.find('h2').text()).toBe('登入/註冊成功');
  });

  it('應該顯示普通用戶功能', async () => {
    // 模擬普通使用者
    Storage.prototype.getItem = jest.fn((key) => {
      if (key === 'role') return 'user';
      return null;
    });

    const wrapper = mount(Dashboard);
    await wrapper.vm.$nextTick();

    // 檢查是否顯示普通用戶內容
    expect(wrapper.find('h3').text()).toBe('普通用戶功能');
    expect(wrapper.text()).toContain('您是普通用戶，您只能查看自己的資料。');
  });

  it('應該顯示管理員功能', async () => {
    // 模擬管理員
    Storage.prototype.getItem = jest.fn((key) => {
      if (key === 'role') return 'admin';
      return null;
    });

    const wrapper = mount(Dashboard);
    await wrapper.vm.$nextTick();

    // 檢查是否顯示管理員內容
    expect(wrapper.find('h3').text()).toBe('管理員功能');
    expect(wrapper.text()).toContain('您擁有管理員權限，可以查看所有使用者的資料。');
  });

  it('應該正確加載用戶數據', async () => {
    expect(axios.get).toHaveBeenCalledWith('/api/users', { withCredentials: true });

    const rows = wrapper.findAll('tbody tr');
    expect(rows.length).toBe(2);

    expect(rows[0].text()).toContain('user1');
    expect(rows[0].text()).toContain('3');
    expect(rows[0].text()).toContain('user');

    expect(rows[1].text()).toContain('admin1');
    expect(rows[1].text()).toContain('10');
    expect(rows[1].text()).toContain('admin');
  });

  it('應該執行登出並清除儲存', async () => {
    await wrapper.find('button').trigger('click');
    await flushPromises();
    await nextTick();
  
    setTimeout(() => {
      expect(sessionStorage.getItem('role')).toBeNull();
    }, 500);
      
    expect(localStorage.getItem('token')).toBeNull();
    expect(sessionStorage.getItem('username')).toBeNull();
    expect(sessionStorage.getItem('lastLogin')).toBeNull();
    expect(sessionStorage.getItem('loginCount')).toBeNull();
  });
});
