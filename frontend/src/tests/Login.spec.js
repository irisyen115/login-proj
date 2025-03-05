import { mount, flushPromises } from '@vue/test-utils';
import { nextTick } from 'vue';
import Login from '../views/LoginView.vue';

const mockPush = jest.fn();
jest.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}));

describe('Login.vue', () => {
  let wrapper;
  
  beforeEach(() => {
    wrapper = mount(Login);
  });

  it('應該正確渲染登入表單', () => {
    expect(wrapper.find('h2').text()).toBe('登入');
    expect(wrapper.find('input[placeholder="帳號"]').exists()).toBe(true);
    expect(wrapper.find('input[placeholder="密碼"]').exists()).toBe(true);
    expect(wrapper.find('button.login-btn').text()).toBe('登入');
  });

  it('應該能夠輸入帳號與密碼', async () => {
    await wrapper.find('input[placeholder="帳號"]').setValue('testUser');
    await wrapper.find('input[placeholder="密碼"]').setValue('password123');

    expect(wrapper.vm.username).toBe('testUser');
    expect(wrapper.vm.password).toBe('password123');
  });

  it('模擬 API 成功回應時，應該跳轉到 /dashboard', async () => {
    global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ token: 'mockToken', role: 'user', last_login: Date.now(), login_count: 1 })
        })
      );
  
      await wrapper.find('input[placeholder="帳號"]').setValue('bbb');
      await wrapper.find('input[placeholder="密碼"]').setValue('222');
      await wrapper.find('form').trigger('submit.prevent');
  
      await flushPromises();
      await nextTick(); 
  
      expect(localStorage.getItem('token')).toBe('mockToken');
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });

  it('模擬 API 失敗回應時，應該顯示錯誤訊息', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ error: '登入失敗' })
      })
    );

    const usernameInput = wrapper.find('input[placeholder="帳號"]');
    const passwordInput = wrapper.find('input[placeholder="密碼"]');

    expect(usernameInput.exists()).toBe(true);
    expect(passwordInput.exists()).toBe(true);

    await usernameInput.setValue('testuser');
    await passwordInput.setValue('wrongpassword');

    await wrapper.find('form').trigger('submit.prevent');

    await flushPromises();
    await nextTick();

    const errorElement = wrapper.find('.error');
    expect(errorElement.exists()).toBe(true); 
    expect(errorElement.text()).toBe('登入失敗');
  });
  
});
