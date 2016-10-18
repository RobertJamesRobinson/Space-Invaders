from pygame.locals import *
import pygame
from random import randint

class SpaceInvaders:
    def __init__(self):
        pygame.mixer.pre_init(22050,-8,2,16)
        pygame.init()
        self.screen=pygame.display.set_mode((1244,850))
        self.sound_player_dies=pygame.mixer.Sound('audio/sound_player_dies.ogg')
        self.sound_alien_advance=pygame.mixer.Sound('audio/sound_alien_advance.ogg')
        self.sound_alien_dies=pygame.mixer.Sound('audio/sound_alien_dies.ogg')
        self.sound_gun_fires=pygame.mixer.Sound('audio/sound_gun_fires.ogg')
        self.sound_mother_ship_flying=pygame.mixer.Sound('audio/sound_mother_ship_flying.ogg')
        self.alienAdvanceEvent=USEREVENT+1
        self.screenRefreshEvent=USEREVENT+2
        self.alienExplosionEvent=USEREVENT+3
        self.alienFireEvent=USEREVENT+4
        self.alienMotherShipEvent=USEREVENT+5
        
        self.advance_speed={0:0,1:530,2:350,3:260,4:190,5:130,6:60}
        self.pixelToSpeedMapping={0:0,1:8,2:12,3:16,4:20,5:24,6:32}
        self.aliensMovingRight=True
        aliens_row1=self.resetAliens(1)
        aliens_row2=self.resetAliens(2)
        aliens_row3=self.resetAliens(3)
        aliens_row4=self.resetAliens(4)
        aliens_row5=self.resetAliens(5)
        aliens_row6=self.resetAliens(6)
        
        self.aliens=[aliens_row1,aliens_row2,aliens_row3,aliens_row4,aliens_row5,aliens_row6]
        self.alienStep=0
        self.black=pygame.Color('#000000')
        self.groundColour=pygame.Color('#4e5516')
        self.leftMarkerColour=pygame.Color('#2e8533')
        self.rightMarkerColour=pygame.Color('#9e8137')
        
        self.gunFiring=False
        self.gunKilled=False
        self.gunMoving="none"
        self.bulletX=0
        self.bulletY=0
        self.alienBulletX=0
        self.alienBulletY=0
        self.alienBulletFiring=False
        self.gunX=270
        self.gunY=708
        self.gunMoveSpeed=14
        self.bulletSpeed=18
        self.gunDeathFrameCount=0
        self.gunDeathFrame=0
        self.aliensLanded=False
        self.motherShipX=1244
        self.motherShipY=5
        self.motherShipFlying=False
        self.motherShipDying=False
        self.motherShipExplosionFrame=0
        self.motherShipFlyingLeft=True
        
        #load the alien sprites
        alienR1Sprites=[pygame.image.load('images/alien_1a.png'),pygame.image.load('images/alien_1b.png')]
        alienR2Sprites=[pygame.image.load('images/alien_2a.png'),pygame.image.load('images/alien_2b.png')]
        alienR3Sprites=[pygame.image.load('images/alien_3a.png'),pygame.image.load('images/alien_3b.png')]
        alienR4Sprites=[pygame.image.load('images/alien_4a.png'),pygame.image.load('images/alien_4b.png')]
        alienR5Sprites=[pygame.image.load('images/alien_5a.png'),pygame.image.load('images/alien_5b.png')]
        alienR6Sprites=[pygame.image.load('images/alien_6a.png'),pygame.image.load('images/alien_6b.png')]
        self.alienSprites=[alienR1Sprites,alienR2Sprites,alienR3Sprites,alienR4Sprites,alienR5Sprites,alienR6Sprites]
        
        #load the gun sprite
        self.gunSprite=pygame.image.load('images/gun.png')
        
        #load the mothership sprite
        self.mothershipSprite=pygame.image.load('images/mothership.png')
        
        #load the shield sprites, 3 of them so we can update each of them with damage as we play
        self.shields=[{'sprite':pygame.image.load('images/shield.png'),'rect':pygame.Rect(336,596,64,72)},{'sprite':pygame.image.load('images/shield.png'),'rect':pygame.Rect(590,596,64,72)},{'sprite':pygame.image.load('images/shield.png'),'rect':pygame.Rect(844,596,64,72)}]
        self.shieldsUp=True
        
        #load the bullet image
        self.bulletSprite=pygame.image.load('images/bullet.png')
        
        #load the explosion sprites
        self.alienExplosionSprites=[pygame.image.load('images/alien_explosion_1.png'),pygame.image.load('images/alien_explosion_2.png'),pygame.image.load('images/alien_explosion_3.png'),pygame.image.load('images/alien_explosion_4.png')]
        
        #load the mothership explosion sprites
        self.mothershipExplosionSprites=[pygame.image.load('images/mothership_explosion_1.png'),pygame.image.load('images/mothership_explosion_2.png')]
        
        self.current_speed=1
        
        #draw the game screen (ground and edge markers)
        groundRect=pygame.Rect(0,748,1244,102)
        leftEdgeRect=pygame.Rect(261,748,18,24)
        rightEdgeRect=pygame.Rect(965,748,18,24)
        self.screen.fill(self.groundColour,groundRect)
        self.screen.fill(self.leftMarkerColour,leftEdgeRect)
        self.screen.fill(self.rightMarkerColour,rightEdgeRect)
        for shield in self.shields:
            self.screen.blit(shield['sprite'],shield['rect'])
        self.drawGun()
        pygame.display.flip()
        
        
    def run(self):
        running=True
        gameClock=pygame.time.Clock()
        pygame.time.set_timer(self.alienAdvanceEvent,self.advance_speed[self.current_speed])
        pygame.time.set_timer(self.screenRefreshEvent,50)
        pygame.time.set_timer(self.alienExplosionEvent,130)
        pygame.time.set_timer(self.alienFireEvent,3000)
        pygame.time.set_timer(self.alienMotherShipEvent,15000)
        
        #main game loop starts
        while running:
            updates=[]
            eventList=pygame.event.get()
            for event in eventList:
                
                #TODO: any functions called in the loop which update screen areas should return a list of rects, to be added to a list which is cleared at the start of each loop
                #      This would allow us to do a single screen update, only on affected areas, once, at the end of each game loop, instead of several times within 1 loop.
                #      This should clean up redraw issues and timing problems during game play
                
                #handle the default quit event
                if event.type==QUIT:
                    running=False
                    
                #hanld ekeyboard events
                if event.type==KEYDOWN:
                    if event.key==K_LEFT:
                        self.gunMoving="left"
                        
                    if event.key==K_RIGHT:
                        self.gunMoving="right"
                        
                    if event.key==K_SPACE:
                        if not self.gunFiring and not self.gunKilled:
                            self.sound_gun_fires.play()
                            self.fireGun()
                            
                if event.type==KEYUP:
                    if event.key==K_LEFT and self.gunMoving=="left":
                        self.gunMoving="none"
                    if event.key==K_RIGHT and self.gunMoving=="right":
                        self.gunMoving="none"
                            
                
                #update any explosion states
                if event.type==self.alienExplosionEvent:
                    self.updateAlienExplosions()
                    updates+=self.updateMotherShipExplosions()
                    
                #aliens advance
                if event.type==self.alienAdvanceEvent and not self.gunKilled and not self.aliensLanded:
                    self.sound_alien_advance.play()
                    updates+=self.moveAliens()
                    
                #mother ship appears
                if event.type==self.alienMotherShipEvent and not self.motherShipFlying:
                    self.triggerMotherShip()
                    
                #aliens fire back
                if event.type==self.alienFireEvent and not self.alienBulletFiring and not self.gunKilled and not self.aliensLanded:
                    self.initiateAlienFiring()
                    
                #screen update
                if event.type==self.screenRefreshEvent:
                    if self.gunMoving=="left" and not self.gunKilled and not self.aliensLanded:
                        updates+=self.moveGunLeft()
                    if self.gunMoving=="right" and not self.gunKilled and not self.aliensLanded:
                        updates+=self.moveGunRight()
                    if self.motherShipFlying:
                        updates+=self.updateMotherShipPos()
                    if self.gunFiring:
                        updates+=self.updateBullet()
                    if self.alienBulletFiring:
                        updates+=self.updateAlienBullet()
                    if self.gunKilled:
                        updates+=self.animateGunDeath()
                    if self.aliensLanded:
                        print "game over"
                        
                        
            gameClock.tick(40)      
            pygame.display.update(updates)
        
    def killAlien(self,row,col):
        self.aliens[row][col][0]=2
        
    def triggerMotherShip(self):
        self.motherShipFlying=True
        pygame.time.set_timer(self.alienMotherShipEvent,0)
        self.sound_mother_ship_flying.play(loops = -1)
        if self.motherShipFlyingLeft:
            self.motherShipX=1244
        else:
            self.motherShipX=-self.mothershipSprite.get_width()
    
    def updateMotherShipExplosions(self):
        explosionFrameLimit=15
        updates=[]
        if self.motherShipDying:
            
            if self.motherShipExplosionFrame==0:
                self.sound_mother_ship_flying.stop()
                self.sound_alien_dies.play()
                self.motherShipFlyingLeft=not self.motherShipFlyingLeft
                motherShipRect=pygame.Rect(self.motherShipX,self.motherShipY,self.mothershipSprite.get_width(),self.mothershipSprite.get_height())
                self.screen.fill(self.black,motherShipRect)
                updates.append(motherShipRect)
            else:
                motherShipRect=pygame.Rect(self.motherShipX,self.motherShipY,self.mothershipExplosionSprites[0].get_width(),self.mothershipExplosionSprites[0].get_height())
                self.screen.fill(self.black,motherShipRect)
                
            
            if self.motherShipExplosionFrame<=explosionFrameLimit:
                if self.motherShipExplosionFrame%2==0:
                    self.screen.blit(self.mothershipExplosionSprites[0],motherShipRect)
                else:
                    self.screen.blit(self.mothershipExplosionSprites[1],motherShipRect)
                    
            else:
                self.motherShipDying=False
                pygame.time.set_timer(self.alienMotherShipEvent,15000)
                self.motherShipExplosionFrame=0
                
            updates.append(motherShipRect)
                
            if self.motherShipDying:
                self.motherShipExplosionFrame+=1
        return updates
        
    def animateGunDeath(self):
        updates=[]
        self.gunDeathFrameCount+=1
        if self.gunDeathFrameCount%3==0:
            self.gunDeathFrame=1-self.gunDeathFrame
            if self.gunDeathFrame==1:
                print "gun death frame 1"
            else:
                print "gun death frame 0"
                
        if self.gunDeathFrameCount==40:
            updates+=self.resetGun()
            
        return updates
        
    def resetGun(self):
        #reset the gun to the left side
        updates=[]
        updates+=self.clearGun()
        self.gunKilled=False
        self.gunMoving="none"
        self.gunDeathFrameCount=0
        self.gunDeathFrame=0
        self.gunX=270
        self.gunY=708
        updates+=self.drawGun()
        return updates
        
    def updateMotherShipPos(self):
        updates=[]
        #remove the sprite
        if not self.motherShipDying:
            blanker=pygame.Rect(self.motherShipX,self.motherShipY,self.mothershipSprite.get_width(),self.mothershipSprite.get_height())
            self.screen.fill(self.black,blanker)
            
            #update the position
            if self.motherShipFlyingLeft:
                self.motherShipX-=5
                if self.motherShipX<-self.mothershipSprite.get_width():
                    self.motherShipFlying=False
                    pygame.time.set_timer(self.alienMotherShipEvent,15000)
                    self.sound_mother_ship_flying.stop()
                    self.motherShipFlyingLeft=not self.motherShipFlyingLeft
                    
            else:
                self.motherShipX+=5
                if self.motherShipX>1244:
                    self.motherShipFlying=False
                    pygame.time.set_timer(self.alienMotherShipEvent,15000)
                    self.sound_mother_ship_flying.stop()
                    self.motherShipFlyingLeft=not self.motherShipFlyingLeft
                
            #redraw the sprite
            if self.motherShipFlying:
                redraw=pygame.Rect(self.motherShipX,self.motherShipY,self.mothershipSprite.get_width(),self.mothershipSprite.get_height())
                self.screen.blit(self.mothershipSprite,redraw)
                updates+=[blanker,redraw]
                
            else:
                updates+=[blanker]
        return updates
            
        
    def moveGunRight(self):
        updates=[]
        updates+=self.clearGun()
        self.gunX+=self.gunMoveSpeed
        if self.gunX>918:
            self.gunX=918
        updates+=self.drawGun()
        return updates
        
    def moveGunLeft(self):
        updates=[]
        updates+=self.clearGun()
        self.gunX-=self.gunMoveSpeed
        if self.gunX<270:
            self.gunX=270
        updates+=self.drawGun()
        return updates
        
    def initiateAlienFiring(self):
        #find an alien to shoot, should be on the lowest row for any column
        availableAliens={}
        for alienRow in range(len(self.aliens)):
            for alienCol in range(len(self.aliens[alienRow])):
                alien=self.aliens[alienRow][alienCol]
                if alien[0]==1:
                    availableAliens[alienCol]=[alien[1]+(self.alienSprites[alienRow][0].get_width()/2-self.bulletSprite.get_width()/2),alien[2]+self.alienSprites[alienRow][0].get_height()]
        
        listOfAliens=availableAliens.items()
        if len(listOfAliens)>0:
            myShooter=listOfAliens[randint(0,len(listOfAliens)-1)]
            
            #set the game logic accordingly
            self.alienBulletX=myShooter[1][0]
            self.alienBulletY=myShooter[1][1]
            self.alienBulletFiring=True
        
    def checkShieldHits(self,bulletRect):
        if self.shieldsUp:
            for shield in self.shields:
                shieldMask=pygame.mask.from_surface(shield['sprite'])
                bulletMask=pygame.mask.from_surface(self.bulletSprite)
                xOffset=bulletRect[0]-shield['rect'][0]
                yOffset=bulletRect[1]-shield['rect'][1]
                myOverlap=shieldMask.overlap(bulletMask,(xOffset,yOffset))
                
                if myOverlap:
                    hitMask=shieldMask.overlap_mask(bulletMask,(xOffset,yOffset))
                    boundingRect=hitMask.get_bounding_rects()[0]
                    shield['sprite'].fill(pygame.Color('#00000000'),boundingRect)
                    self.screen.blit(shield['sprite'],shield['rect'])
                    return True
        return False
        
    def clearShields(self):
        updates=[]
        for shield in self.shields:
            self.screen.fill(self.black,shield['rect'])
            updates.append(shield['rect'])
            
    def updateBullet(self):
        updates=[]
        bulletRect=pygame.Rect(self.bulletX,self.bulletY,self.bulletSprite.get_width(),self.bulletSprite.get_height())
        self.screen.fill(self.black,bulletRect)
        self.bulletY-=self.bulletSpeed
        if self.bulletY<0:
            self.gunFiring=False
            updates.append(bulletRect)
            return updates
            
        if self.motherShipFlying and not self.motherShipDying:
            hitMotherShip=self.checkBulletCollisionsWithMothership((self.bulletX,self.bulletY))
            if hitMotherShip:
                self.motherShipDying=True
                self.motherShipFlying=False
        
        if self.checkShieldHits(bulletRect):
            self.gunFiring=False
            updates.append(bulletRect)
            return updates
            
        impacts=self.checkBulletCollisionsWithAliens((self.bulletX,self.bulletY))
        for impact in impacts:
            self.killAlien(impact[0],impact[1])
        
        if len(impacts)>0:
            self.sound_alien_dies.play()
            self.gunFiring=False
            updates.append(bulletRect)
        else:
            bulletRect2=pygame.Rect(self.bulletX,self.bulletY,self.bulletSprite.get_width(),self.bulletSprite.get_height())
            self.screen.blit(self.bulletSprite,bulletRect2)
            updates+=[bulletRect,bulletRect2]
        return updates
            
    def updateAlienBullet(self):
        updates=[]
        bulletRect=pygame.Rect(self.alienBulletX,self.alienBulletY,self.bulletSprite.get_width(),self.bulletSprite.get_height())
        self.screen.fill(self.black,bulletRect)
        self.alienBulletY+=self.bulletSpeed
        if self.alienBulletY>(748-self.bulletSprite.get_height()):
            self.alienBulletFiring=False
            updates.append(bulletRect)
            return updates
            
        if self.checkShieldHits(bulletRect):
            self.alienBulletFiring=False
            updates.append(bulletRect)
            return updates
            
        #if the bullet hit the gun, kill the gun, otherwise redraw the bullet in its new spot
        if self.checkAlienBulletCollisionWithGun((self.alienBulletX,self.alienBulletY)):
            self.gunKilled=True
            self.sound_alien_dies.play()
            self.alienBulletFiring=False
            updates.append(bulletRect)
            
        else:
            bulletRect2=pygame.Rect(self.alienBulletX,self.alienBulletY,self.bulletSprite.get_width(),self.bulletSprite.get_height())
            self.screen.blit(self.bulletSprite,bulletRect2)
            updates+=[bulletRect,bulletRect2]
        return updates
        
    def fireGun(self):
        #set the starting position of the bullet, set the bullets mode to firing
        self.bulletY=self.gunY-self.bulletSprite.get_height()
        self.bulletX=self.gunX+24
        self.gunFiring=True
        
    def clearGun(self):
        tmp=pygame.Rect(self.gunX,self.gunY,self.gunSprite.get_width(),self.gunSprite.get_height())
        self.screen.fill(self.black,tmp)
        return [tmp]
        
    def drawGun(self):
        tmp=pygame.Rect(self.gunX,self.gunY,self.gunSprite.get_width(),self.gunSprite.get_height())
        self.screen.blit(self.gunSprite,tmp)
        return [tmp]
        
    def checkBulletCollisionsWithAliens(self,bulletPos):
        bulletRect=pygame.Rect(bulletPos[0],bulletPos[1],self.bulletSprite.get_width(),self.bulletSprite.get_height())
        impacts=[]
        for alienRow in range(len(self.aliens)):
            for alienCol in range(len(self.aliens[alienRow])):
                alien=self.aliens[alienRow][alienCol]
                if alien[0]==1:
                    tmp=pygame.Rect(alien[1],alien[2],64,40)
                    if bulletRect.colliderect(tmp):
                        impacts.append((alienRow,alienCol))
        return impacts
        
    def checkBulletCollisionsWithMothership(self,bulletPos):
        bulletRect=pygame.Rect(bulletPos[0],bulletPos[1],self.bulletSprite.get_width(),self.bulletSprite.get_height())
        tmp=pygame.Rect(self.motherShipX,self.motherShipY,self.mothershipSprite.get_width(),self.mothershipSprite.get_height())
        if bulletRect.colliderect(tmp):
            return True
        else:
            return False
        
    def checkAlienBulletCollisionWithGun(self,bulletPos):
        bulletRect=pygame.Rect(bulletPos[0],bulletPos[1],self.bulletSprite.get_width(),self.bulletSprite.get_height())
        tmp=pygame.Rect(self.gunX,self.gunY,self.gunSprite.get_width(),self.gunSprite.get_height())
        if bulletRect.colliderect(tmp):
            return True
        return False
                    
    def moveAliens(self):
        screenUpdateAreas=[]
        screenUpdateAreas+=self.removeAlienSpritesFromScreen()
        onePixel=self.pixelToSpeedMapping[self.current_speed]
        horizontalThresholdR=990
        horizontalThresholdL=190
        liveCounter=0
        
        #shift all aliens in direction of movement by "onePixel"
        switchedDirection=False
        for alienRow in self.aliens:
            for alien in alienRow:
                if alien[0]!=0:
                    if alien[0]==1:
                        liveCounter+=1
                        
                    if self.aliensMovingRight:
                        alien[1]+=onePixel
                        if alien[1]>=horizontalThresholdR:
                            switchedDirection=True
                    else:
                        alien[1]-=onePixel
                        if alien[1]<=horizontalThresholdL:
                            switchedDirection=True
                            
        #adjust speed of invasion accordingly
        newSpeed=1
        if liveCounter<22:
            newSpeed=2
        if liveCounter<8:
            newSpeed=3
        if liveCounter<5:
            newSpeed=4
        if liveCounter<4:
            newSpeed=5
        if liveCounter<2:
            newSpeed=6
        if liveCounter==0:
            newSpeed=0
            
        if self.current_speed!=newSpeed:
            self.current_speed=newSpeed
            pygame.time.set_timer(self.alienAdvanceEvent,self.advance_speed[self.current_speed])
            
                            
        #handle the case where we hit a "wall" and need to change direction
        if switchedDirection:
            for alienRow in self.aliens:
                for alien in alienRow:
                    if alien[0]!=0:
                        alien[2]+=40
                        if alien[2]>=674:
                            self.aliensLanded=True
                        if alien[2]>=556 and self.shieldsUp:
                            self.shieldsUp=False
                            self.clearShields()
            self.aliensMovingRight=not self.aliensMovingRight
            
        #draw the aliens in their new positions, and update the screen
        screenUpdateAreas+=self.drawAlienSpritesToScreen()
        return screenUpdateAreas
        
        
    def updateAlienExplosions(self):
        updateAreas=[]
        for alienRow in self.aliens:
            for alien in alienRow:
                if alien[0]==2:
                    tmp=pygame.Rect(alien[1],alien[2],64,40)
                    updateAreas.append(tmp)
                    self.screen.fill(self.black,tmp)
                    if alien[3]<4:
                        self.screen.blit(self.alienExplosionSprites[alien[3]],tmp)
                        
                        alien[3]+=1
                    else:
                        alien[0]=0
                    
        return updateAreas
        
    def removeAlienSpritesFromScreen(self):
        areaUpdates=[]
        for alienRow in self.aliens:
            for alien in alienRow:
                if alien[0]==1 or alien[0]==2:
                    tmp=pygame.Rect(alien[1],alien[2],64,40)
                    self.screen.fill(self.black,tmp)
                    areaUpdates.append(tmp)
        return areaUpdates
        
    def drawAlienSpritesToScreen(self):
        areaUpdates=[]
        for alienRow in range(6):
            for alien in self.aliens[alienRow]:
                if alien[0]==1:
                    tmp=pygame.Rect(alien[1],alien[2],64,40)
                    self.screen.blit(self.alienSprites[alienRow][self.alienStep],tmp)
                    areaUpdates.append(tmp)
        self.alienStep=1-self.alienStep
        return areaUpdates
                    
                    
    def getSpeed(self,numberOfAliens):
        speed=1
        if numberOfAliens<22:
            speed=2
        if numberOfAliens<8:
            speed=3
        if numberOfAliens<5:
            speed=4
        if numberOfAliens<4:
            speed=5
        if numberOfAliens<2:
            speed=6
            
    def resetAliens(self,row):
        yVal=row*72+26
        return [[1,190,yVal,0],[1,318,yVal,0],[1,446,yVal,0],[1,574,yVal,0],[1,702,yVal,0],[1,830,yVal,0]]
        
app=SpaceInvaders()
app.run()
