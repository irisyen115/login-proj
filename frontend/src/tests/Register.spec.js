import { mount, flushPromises } from '@vue/test-utils';
import { nextTick } from 'vue';
import Register from '../views/RegisterView.vue';

const mockPush = jest.fn();
jest.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}));

describe('Register.vue', () => {
  let wrapper;
  
  beforeEach(() => {
    wrapper = mount(Register);
  });

  it('應該正確渲染註冊表單', () => {
    expect(wrapper.find('h2').text()).toBe('註冊');
    expect(wrapper.find('input[placeholder="帳號"]').exists()).toBe(true);
    expect(wrapper.find('input[placeholder="密碼"]').exists()).toBe(true);
    expect(wrapper.find('button.register-btn').text()).toBe('註冊');
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

    const generateRandomString =
    () => {
      let str = "abcdefghijklmnopqrstuvwxyz";
      let strLen = str.length;
      let result = "";
      
      for (let i = 0; i < 3; i++) {
          result += str[Math.floor(Math.random() * strLen)];
      }    
      return result;
    }
      
    console.log(generateRandomString());
    

    await wrapper.find('input[placeholder="帳號"]').setValue(generateRandomString());
    await wrapper.find('input[placeholder="密碼"]').setValue(generateRandomString());
    await wrapper.find('form').trigger('submit.prevent');

    await flushPromises();
    await nextTick(); 

    expect(localStorage.getItem('token')).toBe('mockToken');
    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it("顯示錯誤訊息當帳號或密碼為空", async () => {
    wrapper.vm.username = "";
    wrapper.vm.password = "";
  
    await wrapper.find("button").trigger("click");
  
    expect(wrapper.text()).toContain("帳號和密碼不能為空");
  });
    
  it("顯示錯誤訊息當只有帳號為空", async () => {
    wrapper.vm.username = "";
    wrapper.vm.password = "password123";
  
    await wrapper.find("button").trigger("click");
  
    expect(wrapper.text()).toContain("帳號和密碼不能為空");
  });
    
  it("顯示錯誤訊息當只有密碼為空", async () => {
    wrapper.vm.username = "user123";
    wrapper.vm.password = "";
  
    await wrapper.find("button").trigger("click");
  
    expect(wrapper.text()).toContain("帳號和密碼不能為空");
  });
});
