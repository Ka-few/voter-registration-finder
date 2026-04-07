from bot import invoke_agent

if __name__ == "__main__":
    print("Welcome to IEBC Registration Assistant CLI")
    phone = "+254700000000"
    while True:
        try:
            user_input = input(f"[{phone}]: ")
            if user_input.lower() in ["quit", "exit"]:
                break
            reply = invoke_agent(phone, user_input)
            print(f"[Agent]: {reply}")
        except KeyboardInterrupt:
            break
