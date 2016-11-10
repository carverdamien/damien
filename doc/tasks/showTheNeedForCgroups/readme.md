# We need cgroups to enforce isolation
## What is isolation and why do we need it?

Applications consume resources as they execute. Some application are better at increasing their resource consumption and can thus starve other applications. Isolation prenvent this resource "stealing" from happening by setting absolute or relative limits on how much resources can be consummed by an application.

If performances scale linearly as a function of resources, you could argue:
- on one hand that resources are globaly well used and thus that isolation is unnecessary  but
- on the other hand you could argue that fairness between application is more important, or that the applications which are bad at increasing their resource consumption are more important and thus that isolation is necessary.

But performances don't always scale linearly as a function of resources which means that isolation is the only way to specify how you want the resources to be spent. Without isolation you might not get the best out of what you paid for.