import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ActiveUsers from '@/components/ActiveUsers.vue'

describe('ActiveUsers Component', () => {
  it('renders properly with empty user list', () => {
    const wrapper = mount(ActiveUsers, {
      props: {
        users: [],
        currentUserId: 1
      }
    })

    expect(wrapper.find('.active-users').exists()).toBe(true)
    expect(wrapper.find('.no-users').exists()).toBe(true)
    expect(wrapper.text()).toContain('等待其他用户加入')
  })

  it('displays user count badge correctly', () => {
    const users = [
      { user_id: 1, username: 'Alice' },
      { user_id: 2, username: 'Bob' },
      { user_id: 3, username: 'Charlie' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const badge = wrapper.find('.user-count-badge')
    expect(badge.exists()).toBe(true)
  })

  it('renders user list correctly', () => {
    const users = [
      { user_id: 1, username: 'Alice Smith' },
      { user_id: 2, username: 'Bob Jones' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const userItems = wrapper.findAll('.user-item')
    expect(userItems).toHaveLength(2)
    expect(wrapper.text()).toContain('Alice Smith')
    expect(wrapper.text()).toContain('Bob Jones')
  })

  it('highlights current user', () => {
    const users = [
      { user_id: 1, username: 'Alice' },
      { user_id: 2, username: 'Bob' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const currentUserItem = wrapper.findAll('.user-item')[0]
    expect(currentUserItem.classes()).toContain('current-user')
    expect(currentUserItem.text()).toContain('(你)')
  })

  it('generates correct user initials for single name', () => {
    const users = [
      { user_id: 1, username: 'Alice' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const avatar = wrapper.find('.user-avatar')
    expect(avatar.text()).toBe('AL')
  })

  it('generates correct user initials for full name', () => {
    const users = [
      { user_id: 1, username: 'Alice Smith' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const avatar = wrapper.find('.user-avatar')
    expect(avatar.text()).toBe('AS')
  })

  it('handles missing username gracefully', () => {
    const users = [
      { user_id: 1, username: null }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const avatar = wrapper.find('.user-avatar')
    expect(avatar.text()).toBe('?')
  })

  it('applies consistent colors based on user ID', () => {
    const users = [
      { user_id: 1, username: 'User1' },
      { user_id: 2, username: 'User2' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: null
      }
    })

    const avatars = wrapper.findAll('.user-avatar')
    const color1 = avatars[0].attributes('style')
    const color2 = avatars[1].attributes('style')

    expect(color1).toBeTruthy()
    expect(color2).toBeTruthy()
    expect(color1).not.toBe(color2)
  })

  it('shows status indicator for all users', () => {
    const users = [
      { user_id: 1, username: 'Alice' },
      { user_id: 2, username: 'Bob' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    const statusDots = wrapper.findAll('.status-dot')
    expect(statusDots).toHaveLength(2)

    const statusTexts = wrapper.findAll('.status-text')
    statusTexts.forEach(status => {
      expect(status.text()).toBe('编辑中')
    })
  })

  it('does not show empty state when users are present', () => {
    const users = [
      { user_id: 1, username: 'Alice' }
    ]

    const wrapper = mount(ActiveUsers, {
      props: {
        users,
        currentUserId: 1
      }
    })

    expect(wrapper.find('.no-users').exists()).toBe(false)
    expect(wrapper.find('.user-item').exists()).toBe(true)
  })
})
